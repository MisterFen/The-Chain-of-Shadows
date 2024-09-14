import random
import pygame
import encounters.encounter_functions as encounter_functions

class Encounter:
    def __init__(self, name, trigger_function):
        self.name = name
        self.trigger_function = trigger_function

    def trigger(self, game_manager):
        self.trigger_function(game_manager)

class EncounterManager:
    def __init__(self, game_manager, min_distance=200):
        """
        :param game_manager: To get stage and player info.
        :param min_distance: Minimum distance the player needs to move to trigger a new encounter.
        """
        self.game_manager = game_manager
        self.player = self.game_manager.player
        self.min_distance = min_distance
        self.encounters = []
        self.triggered_encounters = []
        self.last_position = pygame.Vector2(self.player.rect.center)
        self.spawn_chance = 0.1  # 10% chance of triggering an encounter each check

        self.set_encounters_for_stage()
    
    def set_encounters_for_stage(self):
        stage_encounters = encounter_functions.get_stage_encounter_functions(self.game_manager.selected_stage['name'])
        for encounter in stage_encounters:
            self.add_encounter(Encounter(encounter, stage_encounters[encounter]))
        for universal_encounter in encounter_functions.universal_encounter_functions:
            self.add_encounter(Encounter(universal_encounter, encounter_functions.universal_encounter_functions[universal_encounter]))

    def add_encounter(self, encounter):
        self.encounters.append(encounter)

    def update(self):
        # Calculate the distance moved since the last encounter
        current_position = pygame.Vector2(self.player.rect.center)
        distance_moved = current_position.distance_to(self.last_position)

        # If player has moved enough distance, consider triggering an encounter
        if distance_moved >= self.min_distance:
            if random.random() < self.spawn_chance:
                self.trigger_random_encounter()
                self.last_position = current_position

    def trigger_random_encounter(self):
        if self.encounters:
            encounter = random.choice(self.encounters)
            encounter.trigger(self.game_manager)
            self.triggered_encounters.append((encounter, pygame.Vector2(self.player.rect.center)))

    def draw_triggered_encounters(self):
        # Optional: Draw markers or effects where encounters were triggered
        for _, position in self.triggered_encounters:
            pygame.draw.circle(self.game_manager.screen, (255, 0, 0), position, 5)

