import os
import pygame
import random
import helpers
from config.settings import MAPS_IMAGES_ROOT_PATH

TILE_WIDTH = 240
TILE_HEIGHT = 240

class TileManager:
    def __init__(self, game_manager, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT):
        """
        Initialize the TileManager.

        :param game_manager: The game manager object controlling the game state and screen.
        :param tile_width: The width of each tile in pixels.
        :param tile_height: The height of each tile in pixels.
        """
        self.game_manager = game_manager
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tiles = {}
        self.load_tile_images()

    def load_tile_images(self):
        """Load tile images and store them in a dictionary."""
        self.tile_images = []
        tile_path = os.path.join(MAPS_IMAGES_ROOT_PATH, helpers.get_debug_name_of_object(self.game_manager.selected_stage['name']), "tiles")

        for filename in os.listdir(tile_path):
            image_path = os.path.join(tile_path, filename)
            image = helpers.load_image(image_path, convert_alpha=True, use_transparency=False, desired_width=self.tile_width, desired_height=self.tile_height)
            self.tile_images.append(image)

    def get_tile(self, grid_x, grid_y):
        """Retrieve a tile at the given grid position, generating it if necessary."""
        if (grid_x, grid_y) not in self.tiles:
            # Generate a random tile type
            tile_image = random.choice(self.tile_images)
            self.tiles[(grid_x, grid_y)] = tile_image

        return self.tiles[(grid_x, grid_y)]

    def draw(self):
        """Draw visible tiles based on the camera's position."""
        camera_offset = self.game_manager.camera.topleft
        screen_width, screen_height = self.game_manager.screen.get_size()

        # Calculate the range of grid cells that are visible on screen
        start_x = (camera_offset[0] // self.tile_width) - 1
        start_y = (camera_offset[1] // self.tile_height) - 1
        end_x = (camera_offset[0] + screen_width) // self.tile_width + 1
        end_y = (camera_offset[1] + screen_height) // self.tile_height + 1

        for grid_x in range(start_x, end_x + 1):
            for grid_y in range(start_y, end_y + 1):
                tile_image = self.get_tile(grid_x, grid_y)
                screen_x = grid_x * self.tile_width - camera_offset[0]
                screen_y = grid_y * self.tile_height - camera_offset[1]
                self.game_manager.screen.blit(tile_image, (screen_x, screen_y))