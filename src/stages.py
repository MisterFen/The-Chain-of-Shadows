from tile_manager import TileManager
from config.settings import SOUNDS_ROOT_PATH
import os
import helpers

class Stage:
    def __init__(self, game_manager):
        """
        Initialize the Stage class.

        :param game_manager: The game manager object controlling the game state and screen.
        """
        self.game_manager = game_manager
        self.tile_manager = TileManager(game_manager)
        self.name = self.game_manager.selected_stage['name']
        self.music_track_path = os.path.join(SOUNDS_ROOT_PATH, "music", helpers.get_debug_name_of_object(self.game_manager.selected_stage['name'])+"_theme.mp3") 
        self.random_encounter_distance = self.game_manager.selected_stage['random_encounter_distance']
        self.final_boss_name = self.game_manager.selected_stage['final_boss']

    def draw(self):
        """Draw the stage using the tile manager."""
        self.tile_manager.draw()