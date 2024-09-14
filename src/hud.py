import pygame
from config.settings import HEADER_BAR_IMAGE_PATH
from helpers import load_image

class ProgressBar(pygame.sprite.Sprite):
    def __init__(self, width, height, border_color=(255, 255, 255), fill_color=(0, 255, 0)):
        super().__init__()
        self.width = width
        self.height = height
        self.border_color = border_color
        self.fill_color = fill_color

        # Create an empty surface for the progress bar
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update_bar(self, current_value, max_value):
        # Clear the surface
        self.image.fill((0, 0, 0, 0))  # Transparent background

        # Draw the border of the progress bar
        pygame.draw.rect(self.image, self.border_color, (0, 0, self.width, self.height), 2)

        # Calculate the width of the fill based on the current value
        value_ratio = max(current_value / max_value, 0)
        fill_width = int(self.width * value_ratio)

        # Draw the fill of the progress bar
        pygame.draw.rect(self.image, self.fill_color, (1, 1, fill_width - 2, self.height - 2))

class HealthBar(ProgressBar):
    def __init__(self, player, width, height, offset=(0, -20), border_color=(255, 255, 255), fill_color=(0, 255, 0)):
        super().__init__(width, height, border_color, fill_color)
        self.player = player
        self.offset = offset  # Offset from the player's position

    def update(self, camera_offset):
        # Calculate the position of the health bar relative to the player and camera
        self.rect.centerx = self.player.rect.centerx + self.offset[0] - camera_offset[0]
        self.rect.centery = self.player.rect.top + self.offset[1] - camera_offset[1]

        # Update the health bar based on the player's current health
        self.update_bar(self.player.health, self.player.max_health)

class XPBar(ProgressBar):
    def __init__(self, xp_manager, width, height, position, border_color=(255, 255, 255), fill_color=(0, 0, 255), font=None, font_color=(255, 255, 255)):
        super().__init__(width, height, border_color, fill_color)
        self.xp_manager = xp_manager
        self.rect.topleft = position  # Position of the XP bar in the HUD
        
        # Font and color for rendering the level text
        self.font = font if font else pygame.font.Font(None, 36)  # Default font size 36 if no font is provided
        self.font_color = font_color

        # Text surface for the level display
        self.level_surface = None

    def update(self):
        # Update the XP bar based on the player's current XP
        self.update_bar(self.xp_manager.current_xp, self.xp_manager.xp_per_level)

        # Render the level text
        level_text = f"Level: {self.xp_manager.level}"
        self.level_surface = self.font.render(level_text, True, self.font_color)

    def draw(self, screen):
        # Draw the XP bar
        screen.blit(self.image, self.rect)

        # Draw the level text next to the XP bar
        if self.level_surface:
            text_rect = self.level_surface.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
            screen.blit(self.level_surface, text_rect)
        

class HeaderBar(pygame.sprite.Sprite):
    def __init__(self, game_manager, *groups):
        super().__init__(*groups)
        self.game_manager = game_manager
        
        # Load the original header bar image
        self.original_image = load_image(HEADER_BAR_IMAGE_PATH)
        self.rect = self.original_image.get_rect()
        self.width = self.game_manager.screen.get_width()
        self.height = self.rect.height
        
        # Scale the original image to fit the screen width
        self.original_image = pygame.transform.scale(self.original_image, (self.width, self.height))
        
        # Create the image that will be displayed
        self.image = self.original_image.copy()
        
        # Font settings for the text areas
        self.font = pygame.font.Font(None, 36)  # You can customize the font and size
        self.text_color = (252, 252, 252)  # White color for the text

        xp_bar_width = 400
        xp_bar = XPBar(game_manager.player.xp_manager, xp_bar_width, 50, position=(self.width/2 - xp_bar_width/2, 20))
        game_manager.hud_elements.add(xp_bar)

    def update(self):
        # Clear the image by resetting it to the original scaled image
        self.image = self.original_image.copy()
        
        # Render the text for current wave number and enemies defeated
        wave_text = f"Wave: {self.game_manager.current_wave_number}"
        enemies_text = f"Enemies Defeated: {self.game_manager.enemies_defeated}"
        
        wave_surface = self.font.render(wave_text, True, self.text_color)
        enemies_surface = self.font.render(enemies_text, True, self.text_color)

        # Calculate positions for the text areas
        wave_position = (60, 10)  # Top-left corner with some padding
        enemies_position = (self.width - enemies_surface.get_width() - 60, 10)  # Top-right corner with some padding
        
        # Blit the text surfaces onto the header bar image
        self.image.blit(wave_surface, wave_position)
        self.image.blit(enemies_surface, enemies_position)