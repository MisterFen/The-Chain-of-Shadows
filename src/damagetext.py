import pygame
import pygame.freetype  # You can also use pygame.font

class DamageText(pygame.sprite.Sprite):
    def __init__(self, text, position, color=(255, 0, 0), lifespan=1.0):
        super().__init__()
        self.image, self.rect = self.create_text_surface(text, color)
        self.rect.topleft = position
        self.lifespan = lifespan  # Time in seconds for the text to live
        self.elapsed_time = 0

    def create_text_surface(self, text, color):
        font = pygame.freetype.SysFont(None, 24)  # You can specify a specific font and size
        image, rect = font.render(text, color)
        return image, rect

    def update(self, dt):
        self.elapsed_time += dt
        if self.elapsed_time >= self.lifespan:
            self.kill()  # Remove the sprite when its time is up

        # You can add more visual effects here like moving up or fading
        self.rect.y -= 50 * dt  # Example: move up over time