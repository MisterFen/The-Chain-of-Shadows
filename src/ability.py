from abc import ABC, abstractmethod
import helpers
import os
import pygame
from animated_sprite import AnimatedSprite
from config.settings import ABILITIES_IMAGES_ROOT_PATH, GLOBAL_STAGGERED_PROJECTILE_RATE
from damagetext import DamageText
from enum import Enum

class UpgradeRarity(Enum):
    COMMON = "Common"
    RARE = "Rare"
    EPIC = "Epic"

class UpgradeRarityWeights(Enum):
    UpgradeRarity.COMMON.weight = 80
    UpgradeRarity.RARE.weight = 15
    UpgradeRarity.EPIC.weight = 5

class UpgradeType(Enum):
    STAT_INCREASE = 1
    ALTERATION = 2

class AlterationOption:
    def __init__(self, *args, **kwargs):
        option_info = args[0]
        for key in iter(option_info):
            setattr(self, key, option_info[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.type = UpgradeType.ALTERATION

class UpgradeOption:
    def __init__(self, ability, stat, value, rarity):
        self.ability_name = ability.name
        self.rarity = rarity
        self.stat = stat
        self.rarity = rarity
        self.value = value
        self.type = UpgradeType.STAT_INCREASE

        self.description = f"{self.rarity.value.upper()}: Improve {self.stat} for {self.ability_name} by {self.value}"

class Ability(ABC):
    def __init__(self, ability_info, game_manager, ability_owner):
        self.game_manager = game_manager
        self.__dict__.update(ability_info)
        if self.has_animation:
            self.animation_frames = self.get_animation_info()
        self.ability_owner = ability_owner
        
        self.level = 1
        self.upgrade_options = self.populate_upgrade_options()
        self.learnable_alterations = self.populate_learnable_alterations()
        self.queued_projectile_triggers = []
        self.ability_alteration = []

        self.time_since_last_use = 0

    @abstractmethod
    def trigger(self, player):
        pass

    def update(self, dt):
        """Update ability's state."""
        self.time_since_last_use += dt
        temp_list = []
        for queued_trigger in self.queued_projectile_triggers:
            queued_trigger -= dt
            if queued_trigger > 0:
                temp_list.append(queued_trigger)
            else:
                self.spawn_projectile()
        self.queued_projectile_triggers = temp_list

    def can_trigger(self):
        """Check if ability can be triggered."""
        return self.time_since_last_use >= self.cooldown
    
    def get_animation_info(self):
        animation_location = os.path.join(ABILITIES_IMAGES_ROOT_PATH, self.debug_name, "projectile")
        assert os.path.exists(animation_location), f"Unable to find {animation_location}. Is the ability named correctly?"
        return helpers.load_animation_frames(animation_location)
    
    def increase_level(self, amount):
        assert self.max_level < self.level + amount, f"WARNING: Increasing {self.name} level {self.level} past specified max level {self.max_level}"
        self.level += amount
        print(f"{self.name} level increased to {self.level}!")

    def upgrade(self):
        self.level += 1
        #TODO: Add custom upgrade things for each level

    def populate_upgrade_options(self):
        all_upgrade_options = [] #TODO Refactor
        if hasattr(self, "upgrade_data"):
            for common_upgrade in iter(self.upgrade_data['common_upgrades']):
                all_upgrade_options.append(UpgradeOption(self, common_upgrade[0], common_upgrade[1], UpgradeRarity.COMMON))
            for rare_upgrade in iter(self.upgrade_data['rare_upgrades']):
                all_upgrade_options.append(UpgradeOption(self, rare_upgrade[0], rare_upgrade[1], UpgradeRarity.RARE))
            for epic_upgrade in iter(self.upgrade_data['epic_upgrades']):
                all_upgrade_options.append(UpgradeOption(self, epic_upgrade[0], epic_upgrade[1], UpgradeRarity.EPIC))

        return all_upgrade_options
    
    def populate_learnable_alterations(self):
        all_learnable_alterations_options = [] #TODO Refactor
        if hasattr(self, "upgrade_data") and ("common_alterations" in self.upgrade_data.keys()):
            for common_alteration in iter(self.upgrade_data['common_alterations']):
                all_learnable_alterations_options.append(AlterationOption(self.upgrade_data['common_alterations'][common_alteration], rarity=UpgradeRarity.COMMON))
            for rare_alteration in iter(self.upgrade_data['rare_alterations']):
                all_learnable_alterations_options.append(AlterationOption(self.upgrade_data['rare_alterations'][rare_alteration], rarity=UpgradeRarity.RARE))
            for epic_alteration in iter(self.upgrade_data['epic_alterations']):
                all_learnable_alterations_options.append(AlterationOption(self.upgrade_data['epic_alterations'][epic_alteration], rarity=UpgradeRarity.EPIC))

        return all_learnable_alterations_options

    def upgrade_stat(self, stat, value):
        if hasattr(self, stat):
            stat_to_upgrade = getattr(self, stat)
            setattr(self, stat, stat_to_upgrade + value)
    
    def add_alteration(self, alteration):
        self.ability_alteration.append(alteration)

    def spawn_projectile(self):
        pass

    def queue_projectiles(self, num_projectiles, stagger_rate=GLOBAL_STAGGERED_PROJECTILE_RATE):
        for index in range(num_projectiles):
            self.queued_projectile_triggers.append(index * stagger_rate)

class AbilityCollisionSprite(pygame.sprite.Sprite):
    def __init__(self, ability, *groups):
        super().__init__(*groups)
        self.ability = ability
        self.alterations = ability.ability_alteration
        self.angle = 0  # Starting angle in radians
        self.animation = AnimatedSprite(ability.animation_frames, 0, 0, animation_speed=100) #TODO. Better source for animation_speed
        self.duration = self.ability.duration
        self.enemies_hit = 0
        self.enemy_cooldowns = {}
        self.game_manager = ability.game_manager
        self.image = self.animation.image
        self.on_enemy_collision_text = ability.enemy_hit_text if getattr(self.ability, 'enemy_hit_text', None) else str(ability.damage)
        self.player = ability.game_manager.player
        self.rect = self.image.get_rect(center=(self.ability.ability_owner.rect.center))
        self.targets = "enemies"
        self.time_since_spawned = 0
        self.triggers_on_collision = True
        self.play_trigger_sound()

    def can_collide(self, target):
        # Check if the ability can collide with a specific enemy
        return self.enemy_cooldowns.get(target, 0) <= 0

    def on_collision(self, target):
        self.enemy_cooldowns[target] = self.ability.damage_rate

    def update(self, dt):
        self.time_since_spawned += dt
        self.duration -= dt
        self.animation.update()
        self.image = self.animation.image
        if self.triggers_on_collision:
            self.check_for_collision()
        
        # Update cooldowns for each enemy
        for enemy in list(self.enemy_cooldowns):
            self.enemy_cooldowns[enemy] -= dt
            if self.enemy_cooldowns[enemy] <= 0:
                del self.enemy_cooldowns[enemy]  # Remove enemy from cooldown tracking

        # Check if duration has expired and remove the sprite
        if self.time_since_spawned > self.duration:
            self.kill()

    def draw(self, screen):
        screen_pos = self.rect.move(-self.game_manager.camera.topleft[0], -self.game_manager.camera.topleft[1])
        screen.blit(self.image, screen_pos)

    def check_for_collision(self):
        if self.targets == "enemies":
            enemy_sprite_hits = pygame.sprite.spritecollide(self, self.ability.game_manager.all_enemies, dokill=False)
            enemy_sprite_hits.extend(pygame.sprite.spritecollide(self, self.ability.game_manager.all_neutral_npcs, dokill=False))
        if self.targets == "player":
            enemy_sprite_hits = pygame.sprite.spritecollide(self, self.ability.game_manager.player_sprites, dokill=False)
        for enemy in enemy_sprite_hits:
            if self.can_collide(enemy):
                self.on_collision(enemy)
                self.enemies_hit += 1
                damage_text = DamageText(self.on_enemy_collision_text, enemy.rect.topleft)
                self.game_manager.all_sprites.add(damage_text)
        if getattr(self.ability, 'max_hit_count', None):
            if self.enemies_hit >= self.ability.max_hit_count:
                self.kill()
    
    def play_trigger_sound(self):
        self.ability.game_manager.sound_manager.play_sound(self.ability.debug_name+"_cast")