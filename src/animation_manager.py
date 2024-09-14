import os
from helpers import load_image

class AnimationManager():
    def __init__(self, entity, scale=1):
        self.animations_root = entity.animations_root
        self.animations = self.get_animations(scale)
        self.current_animation = self.animations['idle'] # TODO: REVISIT THIS

    def get_animations(self, scale):
        animations = {}
        states = ["idle", "walk", "attack"] #TODO: MAKE THIS BETTER
        for state in states:
            frames = []
            for file_name in os.listdir(self.animations_root):
                file_name_elements = file_name.split("_")
                if file_name_elements[0] == state:
                    frames.append(load_image(os.path.join(self.animations_root, f"{file_name}"), scale_factor=scale))
            animations[state] = Animation(frames)
        return animations
    
    def update(self, dt):
        self.current_animation.update(dt)

    def get_frame(self):
        return self.current_animation.frames[self.current_animation.current_frame_index]


class Animation:
    def __init__(self, frames, frame_duration = 0.3):
        self.frames = frames
        self.frame_duration = frame_duration  # Time between frames
        self.current_time = 0
        self.current_frame_index = 0

    def update(self, dt):
        self.current_time += dt
        if self.current_time >= self.frame_duration:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.current_time = 0

    