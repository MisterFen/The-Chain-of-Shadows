import pygame

class UIManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.font = pygame.font.Font(None, 24)  # You can load a custom font here
        self.speech_box = None
        self.speech_duration = 0
        self.speech_timer = 0
        self.is_showing_speech = False

    def show_speech_box(self, character_name, text, duration):
        """Display a speech box for a certain duration."""
        self.speech_box = {
            "character_name": character_name,
            "text": text
        }
        self.speech_duration = duration
        self.speech_timer = 0
        self.is_showing_speech = True

    def update(self, dt):
        """Update speech box display timer."""
        if self.is_showing_speech:
            self.speech_timer += dt
            if self.speech_timer >= self.speech_duration:
                self.is_showing_speech = False

    def draw(self, screen):
        """Draw the speech box on the screen if it's active."""
        if self.is_showing_speech and self.speech_box:
            # Draw background box (you can customize this with images or fancy graphics)
            box_rect = pygame.Rect(50, screen.get_height() - 100, screen.get_width() - 100, 50)
            pygame.draw.rect(screen, (0, 0, 0), box_rect)
            pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)

            # Draw the character name and text
            character_name = self.speech_box['character_name']
            text = self.speech_box['text']

            name_surf = self.font.render(character_name, True, (255, 255, 255))
            text_surf = self.font.render(text, True, (255, 255, 255))

            screen.blit(name_surf, (box_rect.x + 10, box_rect.y + 5))
            screen.blit(text_surf, (box_rect.x + 10, box_rect.y + 25))