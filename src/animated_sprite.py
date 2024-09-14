import pygame

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, frames, x, y, animation_speed):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_speed = animation_speed
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        now = pygame.time.get_ticks()
        time_since_last_update = now - self.last_update
        if time_since_last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]