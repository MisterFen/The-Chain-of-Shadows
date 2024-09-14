import os
import pygame
from ability_manager import AbilityManager
from animation_manager import AnimationManager
from config.gamestates import GameState
from helpers import create_instance_of_ability, get_debug_name_of_object, load_animation_frames
from hud import HealthBar
from xp_manager import XPManager

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, game_manager):
        super().__init__(game_manager.player_sprites)
        self.game_manager = game_manager
        self.__dict__.update(self.game_manager.selected_character)
        self.abilities = []
        self.ability_manager = AbilityManager(game_manager)
        self.debug_name = get_debug_name_of_object(self.name)
        self.animations_root = os.path.join("assets", "chars", "heroes", self.debug_name, "in_game")
        self.animation_manager = AnimationManager(self)
        self.health = self.max_health
        self.health_bar = HealthBar(self, width=50, height=10)
        self.image = self.animation_manager.get_frame()
        self.rect = self.image.get_rect(topleft=pos)
        self.velocity = pygame.math.Vector2(0, 0)
        self.paralyzed = False
        self.time_paralyzed = 0
        self.paralyze_duration = 0
        self.xp_manager = XPManager(game_manager)
        game_manager.in_game_ui.add(self.health_bar)

        pygame.joystick.init()
        self.controller = None
        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()

        # Abilities
        for ability_string in self.starting_abilities:
            self.add_ability(ability_string)
        
    def update(self, dt):
        self.input()
        if self.paralyzed:
            self.time_paralyzed += dt
        if self.time_paralyzed > self.paralyze_duration:
            self.paralyzed = False
            self.time_paralyzed = 0
        if not self.paralyzed:
            self.move()
        self.trigger_abilities()
        self.animation_manager.update(dt)
        self.image = self.animation_manager.get_frame()

        # Update abilities
        for ability in self.abilities:
            ability.update(dt)

    def gain_xp(self, value):
        self.xp_manager.gain_xp(value)

    def get_pos(self):
        pos = (self.rect.x, self.rect.y)
        return pos
    
    def get_center(self):
        return self.rect.center

    def input(self):
        keys = pygame.key.get_pressed()
        controller_input = False

        if self.controller:
            # Get axis values from the controller
            left_x = self.controller.get_axis(0)
            left_y = self.controller.get_axis(1)

            # Set a threshold to avoid unintended movement due to minor axis drift
            deadzone = 0.2

            if abs(left_x) > deadzone:
                self.velocity.x = left_x
                controller_input = True
            else:
                self.velocity.x = 0

            if abs(left_y) > deadzone:
                self.velocity.y = left_y
                controller_input = True
            else:
                self.velocity.y = 0

        # If no controller input, fall back to keyboard input
        if not controller_input:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.velocity.y = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.velocity.y = 1
            else:
                self.velocity.y = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.velocity.x = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.velocity.x = 1
            else:
                self.velocity.x = 0

    def move(self):
        if self.velocity.magnitude() != 0:
            self.velocity = self.velocity.normalize()
        self.rect.x += self.velocity.x * self.speed
        self.rect.y += self.velocity.y * self.speed

    def trigger_abilities(self):
        """Method to trigger abilities. Could be called based on game logic."""
        for ability in self.abilities:
            if ability.can_trigger():
                ability.trigger()

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.on_death()

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def on_death(self):
        print("Player has died.")
        self.game_manager.change_state(GameState.GAME_OVER)

    def add_ability(self, ability_name):
        ability_instance = create_instance_of_ability(ability_name, self.game_manager, self)
        self.abilities.append(ability_instance)

    def get_paralyzed(self, duration):
        self.paralyze_duration = duration
        self.paralyzed = True