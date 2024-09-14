import helpers
import os
import pygame
from animated_sprite import AnimatedSprite
from config.settings import ITEM_IMAGES_ROOT_PATH

class Item(pygame.sprite.Sprite):
    def __init__(self, game_manager, id, name, description, score, spawn_pos, *groups):
        super().__init__(*groups)
        animation_location = os.path.join(ITEM_IMAGES_ROOT_PATH, id)
        assert(os.path.exists(animation_location), f"Unable to find {animation_location}. Is the item named correctly?")
        self.animation_frames = helpers.load_animation_frames(animation_location)
        self.animation = AnimatedSprite(self.animation_frames, 0, 0, animation_speed=100) #TODO. Better source for animation_speed
        self.description = description
        self.game_manager = game_manager
        self.image = self.animation.image
        self.rect = self.image.get_rect(center=spawn_pos)
        self.name = name
        self.score = score

    def on_collect(self):
        """Define what happens when the item is used. This will be overridden in subclasses."""
        raise NotImplementedError("This method should be overridden by subclasses")


class Collectible(Item):
    def __init__(self, game_manager, id, name, description, value, score, spawn_pos, *groups):
        super().__init__(id, name, description, score, spawn_pos, *groups)
        self.value = value

    def on_collect(self):
        """Collect the item to increase score or another metric."""
        return f"Collected {self.name} worth {self.value} points."


class XPItem(Item):
    def __init__(self, game_manager, id, name, description, xp_value, score, spawn_pos, *groups):
        super().__init__(game_manager,id, name, description, score, spawn_pos, *groups)
        self.xp_value = xp_value

    def on_collect(self):
        self.game_manager.player.gain_xp(self.xp_value)


class HealingItem(Item):
    def __init__(self, game_manager, id, name, description, icon, rarity, heal_value):
        super().__init__(id, name, description, icon, rarity)
        self.heal_value = heal_value

    def on_collect(self):
        """Heal the player by a certain amount."""
        return f"Healed {self.heal_value} health points."
