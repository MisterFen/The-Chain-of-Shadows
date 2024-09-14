import json
import os
import pygame
from animation_manager import AnimationManager
from config.settings import CUTSCENES_INFO_PATH
from config.gamestates import GameState

class CutsceneCharacter(pygame.sprite.Sprite):
    def __init__(self, game_manager, character_name, animations_root, pos, *groups):
        super().__init__(*groups)
        self.pos = pos
        self.animations_root = os.path.join("assets", animations_root, "in_game")
        self.animation_manager = AnimationManager(self)
        self.image = self.animation_manager.get_frame()
        self.rect = self.image.get_rect(topleft=pos)
    
    def draw(self, screen):
        screen.blit(self.image, self.pos)

    def update(self):
        self.animation_manager.update()  # Ensure this is optimized for smooth updates
        self.image = self.animation_manager.get_frame()  # Always fetch the latest frame

class CutsceneManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.all_cutscene_info = self.get_all_cutscene_info()
        self.running_cutscene = None

    def get_all_cutscene_info(self) -> dict:
        cutscenes_file_path = CUTSCENES_INFO_PATH
        data = dict()
        with open(cutscenes_file_path, 'r') as file:
            data = json.load(file)
        return data

    def start_cutscene(self):
        cutscene_name = self.game_manager.selected_stage['boss_spawn_cutscene']
        cutscene_data = self.all_cutscene_info[cutscene_name]
        if cutscene_data:
            self.running_cutscene = Cutscene(self.game_manager, cutscene_data)

    def update(self, dt):
        if not self.running_cutscene:
            return
        self.running_cutscene.update(dt)
        if self.running_cutscene.cutscene_step_index >= len(self.running_cutscene.cutscene_steps):
            self.running_cutscene.on_end_cutscene()
            self.running_cutscene = None
            self.game_manager.change_state(GameState.BOSS_FIGHT)
            self.game_manager.enemy_manager.boss_manager.start_boss_fight(self.game_manager.stage.final_boss_name)

class Cutscene:
    def __init__(self, game_manager, cutscene_data):
        self.game_manager = game_manager
        self.cutscene_chars = cutscene_data.get("characters", [])
        self.cutscene_steps = cutscene_data.get("commands", [])
        self.cutscene_step_index = 0
        self.time_accumulator = 0
        self.characters = {}
        self.skip_requested = False

    def handle_events(self, events):
        """Handles all events like key presses."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.skip_requested = True

    def update(self, dt):
        """Updates the current cutscene step and manages timing."""
        self.handle_events(pygame.event.get())
        
        if self.skip_requested:
            self.skip_step()

        # Check if we've finished all steps
        if self.cutscene_step_index >= len(self.cutscene_steps):
            return

        current_step = self.cutscene_steps[self.cutscene_step_index]
        self.execute_step(current_step, dt)

    def skip_step(self):
        """Immediately proceed to the next cutscene step."""
        self.skip_requested = False
        self.time_accumulator = 0
        self.cutscene_step_index += 1

    def execute_step(self, step, dt):
        """Executes the current step based on the action type."""
        action = step.get("action")
        if action == "spawn":
            self.handle_spawn(step)
        elif action == "move":
            self.handle_move(step, dt)
        elif action == "speech_box":
            self.handle_speech_box(step)

        # Handle step duration
        duration = step.get("duration", 0)
        if duration > 0:
            self.time_accumulator += dt
            if self.time_accumulator >= duration:
                self.time_accumulator = 0
                self.cutscene_step_index += 1
        else:
            # If no duration, immediately proceed to the next step
            self.cutscene_step_index += 1

    def handle_spawn(self, step):
        """Handles spawning a character in the cutscene."""
        character_name = step.get("character_name")
        animations_root = self.cutscene_chars[character_name]['visuals']
        position = step.get("position", [0, 0])
        self.characters[character_name] = CutsceneCharacter(
            self.game_manager, 
            character_name, 
            animations_root, 
            position, 
            self.game_manager.all_neutral_npcs
        )

    def handle_move(self, step, dt):
        """Handles moving one or more characters."""
        characters_to_move = step.get("characters", [step])  # Single character or list
        all_moves_complete = True
        
        for character_move in characters_to_move:
            character_name = character_move.get("character_name")
            target_position = character_move.get("to", [0, 0])
            duration = character_move.get("duration", 1)
            character = self.characters.get(character_name)

            if character:
                all_moves_complete &= self.move_character(character, target_position, duration, dt)

        # Only move to the next step if all characters have finished moving
        if all_moves_complete:
            self.cutscene_step_index += 1

    def move_character(self, character, target_position, duration, dt):
        """Moves a character towards a target position."""
        start_position = character.pos
        movement = [
            (target_position[0] - start_position[0]) / duration,
            (target_position[1] - start_position[1]) / duration
        ]

        # Move the character for this frame
        character.pos[0] += movement[0] * dt
        character.pos[1] += movement[1] * dt

        # Check if character has reached the target within a small tolerance
        if abs(character.pos[0] - target_position[0]) > 0.1 or abs(character.pos[1] - target_position[1]) > 0.1:
            return False  # Not yet at the destination
        
        return True  # Move complete

    def handle_speech_box(self, step):
        """Displays a speech box for a given character."""
        character_name = step.get("character_name")
        text = step.get("text", "")
        duration = step.get("duration", 3)

        self.game_manager.ui_manager.show_speech_box(character_name, text, duration)

    def on_end_cutscene(self):
        """Cleans up characters at the end of the cutscene."""
        for character_name in self.characters.keys():
            self.characters[character_name].kill()