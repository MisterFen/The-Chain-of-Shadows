import math
import pygame
import random
from ability import Ability, AbilityCollisionSprite
from enum import Enum
from movement_manager import MovementManager

class WardenState(Enum):
    HUNTING = 1
    DASHING = 2

class Soulwarden(Ability):
    def __init__(self, game_manager, ability_owner):
        self.debug_name = "soulwarden"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, ability_owner)
        self.state = WardenState.HUNTING

    def trigger(self):
        self.queue_projectiles(self.projectiles, stagger_rate=self.time_between_projectiles)
        self.time_since_last_use = 0

    def spawn_projectile(self):
        SoulwardenSprite(self, self.game_manager.all_ability_sprites)

class SoulwardenSprite(AbilityCollisionSprite):
    def __init__(self, ability, *groups):
        self.ability = ability
        super().__init__(ability, *groups)
        self.time_since_last_dash = 0
        self.time_for_next_dash = 1
        self.time_since_last_pulse = 0
        self.movement_target = None
        self.state = WardenState.HUNTING

    def update(self, dt):
        super().update(dt)
        self.time_since_last_dash += dt
        self.time_since_last_pulse += dt

        def move_towards_target(target_pos, speed_multiplier=1):
            self.rect.x, self.rect.y = MovementManager.move(
                (self.rect.x, self.rect.y), 
                self.ability.speed * speed_multiplier, 
                dt, 
                target_pos
            )

        if self.state == WardenState.HUNTING:
            closest_enemy = self.game_manager.enemy_manager.get_closest_enemy()
            if closest_enemy:
                move_towards_target((closest_enemy.rect.x, closest_enemy.rect.y))

        elif self.state == WardenState.DASHING and self.movement_target:
            move_towards_target((self.movement_target.x, self.movement_target.y), speed_multiplier=self.warden_dash_alteration.speed_multiplier)

            # Check if dash distance exceeded max range in pixels
            if math.hypot(self.rect.x - self.initial_dash_position[0], self.rect.y - self.initial_dash_position[1]) >= self.warden_dash_alteration.max_distance:
                self.state = WardenState.HUNTING
                self.movement_target = None

        self.warden_dash_alteration = next((x for x in self.alterations if x.debug_name == "warden_dash"), None)
        if self.warden_dash_alteration and self.time_since_last_dash > self.time_for_next_dash:
            self.update_warden_dash()

        self.warden_pulse_alteration = next((x for x in self.alterations if x.debug_name == "warden_pulse"), None)
        if self.warden_pulse_alteration and self.time_since_last_pulse > self.warden_pulse_alteration.time_between_pulses:
            self.trigger_warden_pulse()

        self.warden_constellation_alteration = next((x for x in self.alterations if x.debug_name == "warden_constellation"), None)
        if self.warden_constellation_alteration and self.time_since_last_dash > self.time_for_next_dash:
            self.update_warden_constellation()

    def update_warden_dash(self):
        closest_enemy = self.game_manager.enemy_manager.get_closest_enemy()
        if closest_enemy:
            # Normalize and scale the direction vector
            dx, dy = closest_enemy.rect.x - self.rect.x, closest_enemy.rect.y - self.rect.y
            distance = math.hypot(dx, dy)
            if distance:
                dx, dy = dx / distance, dy / distance

            self.movement_target = pygame.Rect(self.rect.x + dx * 200, self.rect.y + dy * 200, self.rect.width, self.rect.height)
            self.initial_dash_position = (self.rect.x, self.rect.y)
            self.time_since_last_dash = 0
            self.time_for_next_dash = self.warden_dash_alteration.time_between_dashes + random.random()
            self.state = WardenState.DASHING
    
    def trigger_warden_pulse(self):
        pulse_ability = WardenPulseAbility(self.game_manager, damage = self.ability.damage, ability_owner=self.ability.ability_owner)
        pulse_ability.trigger(self.rect.center)
        self.time_since_last_pulse = 0

    def update_warden_constellation(self):
        print("UPDATE WARDEN CONSTELLATION")
        pass

    def on_collision(self, target):
        super().on_collision(target)
        target.take_damage(self.ability.damage)

class WardenPulseAbility(Ability):
    def __init__(self, game_manager, damage, ability_owner):
        self.debug_name = "warden_pulse"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, ability_owner)
        self.damage = damage

    def trigger(self, pos):
        pulse = WardenPulseSprite(self, pos)
        self.game_manager.all_sprites.add(pulse)
        self.time_since_last_use = 0

class WardenPulseSprite(AbilityCollisionSprite):
    def __init__(self, ability, pos):
        self.ability = ability
        super().__init__(ability)
        self.rect.center = pos
    
    def on_collision(self, target):
        super().on_collision(target)
        target.take_damage(self.ability.damage)