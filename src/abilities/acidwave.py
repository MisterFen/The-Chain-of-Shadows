from ability import Ability, AbilityCollisionSprite
from movement_manager import MovementManager
import pygame

class AcidWave(Ability):
    """
    Fires 4 projectiles in either the up/down/left/right directions or diagonally.
    Cycles through these two configurations.
    """
    def __init__(self, game_manager, ability_owner):
        self.debug_name = "acid_wave"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, ability_owner)
        self.cycle_state = 0  # Keeps track of which configuration to fire (0: cardinal, 1: diagonal)

    def trigger(self):
        """
        Triggers the ability by firing 4 projectiles in the current configuration.
        """
        directions = self.get_projectile_directions()  # Get either cardinal or diagonal directions.
        for direction in directions:
            self.queue_projectile(direction)
        
        # Cycle between configurations (0: cardinal, 1: diagonal)
        self.cycle_state = (self.cycle_state + 1) % 2
        self.time_since_last_use = 0

    def get_projectile_directions(self):
        """
        Returns the 4 directions based on the current cycle state.
        Cycle 0: up, down, left, right.
        Cycle 1: diagonal directions (up-left, up-right, down-left, down-right).
        
        Returns:
            List of direction tuples (dx, dy).
        """
        if self.cycle_state == 0:
            return [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, down, left, right
        else:
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonal directions

    def queue_projectile(self, direction):
        """
        Spawns a projectile in a specific direction.
        
        Args:
            direction (tuple): The (dx, dy) direction the projectile will travel.
        """
        AcidWaveSprite(self, direction, self.game_manager.all_ability_sprites)


class AcidWaveSprite(AbilityCollisionSprite):
    """
    Represents the projectile fired by AcidWave.
    Moves in the specified direction and rotates the sprite to face the direction of movement.
    """
    def __init__(self, ability, direction, *groups):
        """
        Initializes the AcidWave projectile and rotates its image to face the direction.
        
        Args:
            ability (AcidWave): Reference to the AcidWave ability.
            direction (tuple): The (dx, dy) direction the projectile will move.
            groups (sprite groups): The groups this sprite will belong to.
        """
        self.ability = ability
        self.direction = direction  # The direction (up, down, left, right, or diagonal)
        super().__init__(ability, *groups)
        self.targets = "player"
        self.target = None  # No specific target; moves in a fixed direction
        
        # Rotate the sprite image based on direction
        self.rotate_sprite()

    def rotate_sprite(self):
        """
        Rotates the projectile's sprite image based on the direction it's moving.
        """
        # Calculate the angle to rotate based on the (dx, dy) direction
        angle = self.calculate_rotation_angle(self.direction)

        # Rotate the sprite image by the calculated angle
        rotated_image = pygame.transform.rotate(self.animation.image, angle)
        
        # Set colorkey again if needed (assuming transparency is defined in load_image)
        if self.image.get_colorkey() is not None:
            rotated_image.set_colorkey(self.image.get_colorkey())

        # Recompute rect after rotation (to avoid position misalignment)
        self.rect = rotated_image.get_rect(center=self.rect.center)

        # Replace the image with the newly rotated image
        self.image = rotated_image

    def calculate_rotation_angle(self, direction):
        """
        Calculates the angle of rotation based on the direction of movement.
        
        Args:
            direction (tuple): The (dx, dy) direction tuple.
        
        Returns:
            float: The angle in degrees to rotate the image.
        """
        # Map direction to the corresponding rotation angle
        if direction == (0, -1):  # Up
            return 0
        elif direction == (0, 1):  # Down
            return 180
        elif direction == (-1, 0):  # Left
            return 90
        elif direction == (1, 0):  # Right
            return -90
        elif direction == (-1, -1):  # Up-left (diagonal)
            return 45
        elif direction == (-1, 1):  # Down-left (diagonal)
            return 135
        elif direction == (1, -1):  # Up-right (diagonal)
            return -45
        elif direction == (1, 1):  # Down-right (diagonal)
            return -135
        else:
            return 0  # Default case, no rotation

    def update(self, dt):
        """
        Updates the position of the projectile and rotates it based on the direction.
        
        Args:
            dt (float): Delta time for frame-based movement.
        """
        # Call the parent update (which handles animation updates)
        super().update(dt)
        
        # Move in the specified direction
        self.rect.x, self.rect.y = MovementManager.move((self.rect.x, self.rect.y), self.ability.speed, dt, direction=self.direction)
        
        # Rotate the sprite after updating the animation
        self.rotate_sprite()

    def on_collision(self, target):
        """
        Handles what happens when the projectile collides with a target.
        
        Args:
            target: The object it collided with.
        """
        super().on_collision(target)
        target.take_damage(self.ability.damage)  # Deal damage to the target on collision