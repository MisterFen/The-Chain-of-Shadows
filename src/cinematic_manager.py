import pygame
import json
import sys
from config.settings import CINEMATICS_INFO_PATH, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from config.gamestates import GameState
from helpers import load_image

class CinematicManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.screen = game_manager.screen

        # Load cinematic data from JSON
        with open(CINEMATICS_INFO_PATH) as file:
            self.cinematics_data = json.load(file)

        self.current_cinematic = None
        self.background_image = None
        self.text_lines = []
        self.vo_lines = []
        self.scroll_speed = 0
        self.bg_x = 0
        self.current_line_index = 0
        self.text_box_rect = pygame.Rect(50, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 100, 100)

        # Keep track of whether a VO line is currently playing
        self.vo_playing = False

    def load_cinematic(self, cinematic_name):
        cinematic_data = self.cinematics_data[cinematic_name]
        self.background_image = load_image(image_path = cinematic_data["image_path"], desired_width=SCREEN_WIDTH * 1.2,desired_height=SCREEN_HEIGHT)
        self.text_lines = cinematic_data["text_lines"]
        self.vo_lines = cinematic_data["vo_lines"]
        self.scroll_speed = cinematic_data["scroll_speed"]

        # Start playing the first VO line
        self.current_line_index = 0
        self.play_vo_line()

    def play_vo_line(self):
        if self.current_line_index < len(self.vo_lines):
            self.game_manager.sound_manager.play_vo_line(self.vo_lines[self.current_line_index])
            self.vo_playing = True
            self.current_line_index += 1
        else:
            self.vo_playing = False  # No more VO lines to play

    def update(self):
        # Scroll the background image until it reaches the end
        if self.bg_x > -self.background_image.get_width() + SCREEN_WIDTH:
            self.bg_x -= self.scroll_speed

        # If the VO line is done playing, start the next one
        if not pygame.mixer.get_busy() and self.vo_playing:
            self.play_vo_line()

    def draw(self):
        # Draw the scrolling background image
        self.screen.blit(self.background_image, (self.bg_x, 0))

        # Draw the text box
        pygame.draw.rect(self.screen, (0, 0, 0), self.text_box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.text_box_rect, 2)

        # Draw the current text line
        font = pygame.font.Font(None, 36)
        if self.current_line_index > 0:
            text_surface = font.render(self.text_lines[self.current_line_index - 1], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.text_box_rect.center)
            self.screen.blit(text_surface, text_rect)

    def play_cinematic(self, cinematic_name):
        self.load_cinematic(cinematic_name)

        # Run the cinematic
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Spacebar to skip to the next VO line
                        if self.vo_playing and self.current_line_index < len(self.vo_lines):
                            self.play_vo_line()  # Play the next VO line immediately
                        else:
                            self.game_manager.sound_manager.stop_vo()
                            running = False  # End cinematic if no lines are left
                    elif event.key == pygame.K_ESCAPE:  # Escape key to exit the cinematic
                        running = False

            self.update()
            self.draw()

            pygame.display.flip()
            self.game_manager.clock.tick(FPS)

            # Exit the cinematic when the last VO line is done
            if self.current_line_index >= len(self.vo_lines) and not self.vo_playing:
                running = False
        self.game_manager.change_state(GameState.NEW_GAME)