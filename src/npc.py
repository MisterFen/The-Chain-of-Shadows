import math
import os
import pygame
from animation_manager import AnimationManager
from loot_manager import ItemTypes
from movement_manager import MovementManager
from enum import Enum

class NPCTypes(Enum):
    ENEMY = "enemies"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"

class NPCStates(Enum):
    IDLE = "idle"
    WALK = "walk"
    ATTACK = "attack"

class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, npc_info, game_manager, *groups):
        super().__init__(*groups)
        self.solid_body = True
        self.__dict__.update(npc_info)
        self.game_manager = game_manager
        self.state = NPCStates.IDLE
        #Visual
        self.animations_root = os.path.join("assets", "npcs", npc_info["type"], npc_info["debug_name"], "in_game")
        self.animation_manager = AnimationManager(self, scale=1.5)
        self.image = self.animation_manager.get_frame()
        self.rect = self.image.get_rect(topleft=pos)
        #Stats
        self.attack_cooldown = 1.0  # Time in seconds between attacks
        self.health = self.base_health
        self.target = None  # Target to chase, usually the player
        self.target_pos = None # Fixed target position to move towards
        self.time_since_last_attack = 0.0
        #GameLogic Stats
        self.time_frozen = 0
        self.freeze_duration = 0
        self.frozen = False
        self.time_controlled = 0
        self.controlled_duration = 0
        self.controlled = False
        self.time_paralyzed = 0
        self.paralyzed_duration = 0
        self.paralyzed = False

    def draw(self, screen):
        screen_pos = self.rect.move(-self.game_manager.camera.topleft[0], -self.game_manager.camera.topleft[1])
        # Get the camera's visible area
        camera_rect = self.game_manager.camera

        # Check if the object is within the camera's view
        if self.rect.colliderect(camera_rect):
            screen.blit(self.image, screen_pos)
        
    def can_attack(self):
        return self.time_since_last_attack > self.attack_cooldown
    
    def update(self, dt):
        if self.solid_body:
            self.avoid_overlap()
        self.time_since_last_attack += dt
        self.time_controlled += dt
        self.animation_manager.update(dt)
        self.image = self.animation_manager.get_frame()

        if self.time_frozen > self.freeze_duration:
            self.frozen = False
        if self.time_controlled > self.controlled_duration:
            self.controlled = False
        if self.time_paralyzed > self.paralyzed_duration:
            self.paralyzed = False

        if self.frozen or self.paralyzed:
            self.time_frozen += dt
            self.time_paralyzed += dt
        
        if self.has_target():
            self.target_pos = self.target.get_pos()
        if self.target_pos:
            if not (self.frozen or self.paralyzed):
                self.set_state(NPCStates.WALK)
                if self.controlled:
                    self.move_away_from_target_pos(dt)
                else:
                    self.move_towards_target_pos(dt)
    
    def take_damage(self, amount):
        """Take damage and reduce health."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.on_death()
    
    def move_towards_target_pos(self, dt):
        self.rect.x, self.rect.y = MovementManager.move((self.rect.x, self.rect.y), self.speed,  dt, target_pos=self.target_pos)

    def move_away_from_target_pos(self, dt):
        self.rect.x, self.rect.y = MovementManager.move_away_from((self.rect.x, self.rect.y), self.speed,  dt, target_pos=self.target_pos)
    
    def set_target(self, target):
        """Set the target for the enemy, typically the player."""
        self.target = target

    def set_target_pos(self, pos):
        """Set the target for the enemy, typically the player."""
        self.target_pos = pos

    def has_target(self):
        return (self.target != None)

    def on_death(self):
        pass

    def set_pos(self, pos):
        self.rect.center = pos

    def get_pos(self):
        return self.rect.center
    
    def set_state(self, state):
        self.state = state
    
    def avoid_overlap(self):
        for other_enemy in self.game_manager.all_enemies:
            if other_enemy != self and other_enemy.solid_body:
                # Check if the mobs overlap
                if self.rect.colliderect(other_enemy.rect):
                    # Calculate the distance and direction between mobs
                    dx = self.rect.centerx - other_enemy.rect.centerx
                    dy = self.rect.centery - other_enemy.rect.centery
                    distance = math.hypot(dx, dy)

                    # Avoid division by zero
                    if distance == 0:
                        distance = 1.0

                    # Calculate the minimum distance to resolve the collision
                    min_distance = self.rect.width / 2 + other_enemy.rect.width / 2

                    # If the mobs are too close, push them apart
                    if distance < min_distance:
                        overlap = min_distance - distance

                        # Normalize the direction vector and push mobs apart
                        push_x = (dx / distance) * overlap / 2
                        push_y = (dy / distance) * overlap / 2

                        self.rect.x += push_x
                        self.rect.y += push_y

                        other_enemy.rect.x -= push_x
                        other_enemy.rect.y -= push_y

class FriendlyNPC(NPC):
    def __init__(self, pos, npc_info, game_manager, *groups):
        self.type = NPCTypes.FRIENDLY
        super().__init__(pos, npc_info, game_manager, *groups)

class TemporalRiftNPC(FriendlyNPC):
    def __init__(self, pos, npc_info, game_manager, *groups):
        super().__init__(pos, npc_info, game_manager, *groups)
        self.time_since_last_mob_spawn = 0
        self.time_since_spawned = 0

    def update(self, dt):
        super().update(dt)
        self.time_since_last_mob_spawn += dt
        self.time_since_spawned += dt
        if self.time_since_last_mob_spawn > self.spawn_interval:
            self.game_manager.enemy_manager.spawn_elite_enemy(self.rect.center)
            self.time_since_last_mob_spawn = 0
        if self.time_since_spawned > self.duration:
            self.kill()

class NeutralNPC(NPC):
    def __init__(self, pos, npc_info, game_manager, *groups):
        self.type = NPCTypes.NEUTRAL
        super().__init__(pos, npc_info, game_manager, *groups)


class FallenStarNPC(NeutralNPC):
    def __init__(self, pos, npc_info, game_manager, *groups):
        super().__init__(pos, npc_info, game_manager, *groups)

    def on_death(self):
        self.game_manager.loot_manager.spawn_event_item(ItemTypes.XP, self.rect.center)
        self.kill()  # Remove the enemy from all sprite groups