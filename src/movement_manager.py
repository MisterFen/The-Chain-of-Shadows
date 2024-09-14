import math
import pygame
import random

class MovementManager:
    @staticmethod
    def calculate_direction(source_pos, target_pos=None, direction=None):
        """
        Calculates the normalized direction vector. Either to a target position or uses a provided direction.

        :param source_pos: The starting position (x, y) tuple.
        :param target_pos: The target position (x, y) tuple. (Optional if direction is provided)
        :param direction: A specified direction vector (pygame.math.Vector2). (Optional if target_pos is provided)
        :return: A normalized direction vector (pygame.math.Vector2).
        """
        if target_pos is not None:
            direction_vector = pygame.math.Vector2(target_pos) - pygame.math.Vector2(source_pos)
        elif direction is not None:
            direction_vector = pygame.math.Vector2(direction)
        else:
            random_angle = random.uniform(0, 2 * math.pi)
            direction_vector = pygame.math.Vector2(math.cos(random_angle), math.sin(random_angle))

        return direction_vector.normalize() if direction_vector.length() != 0 else direction_vector

    @staticmethod
    def move(source_pos, speed, dt, target_pos=None, direction=None):
        """
        Moves the source either towards a target position or in a specified direction.

        :param source_pos: The starting position (x, y) tuple.
        :param speed: The speed at which to move.
        :param dt: Delta time for frame-independent movement.
        :param target_pos: The target position (x, y) tuple. (Optional if direction is provided)
        :param direction: The direction vector (pygame.math.Vector2) to move in. (Optional if target_pos is provided)
        :return: The new position after moving (x, y).
        """
        direction_vector = MovementManager.calculate_direction(source_pos, target_pos, direction)
        movement = direction_vector * speed * dt
        new_position = pygame.math.Vector2(source_pos) + movement
        return new_position.x, new_position.y

    @staticmethod
    def move_away_from(source_pos, speed, dt, target_pos=None, direction=None):
        """
        Moves the source away from a target position or in the opposite of a specified direction.

        :param source_pos: The starting position (x, y) tuple.
        :param speed: The speed at which to move.
        :param dt: Delta time for frame-independent movement.
        :param target_pos: The target position (x, y) tuple. (Optional if direction is provided)
        :param direction: The direction vector (pygame.math.Vector2) to move in. (Optional if target_pos is provided)
        :return: The new position after moving (x, y).
        """
        direction_vector = MovementManager.calculate_direction(source_pos, target_pos, direction)
        movement = direction_vector * speed * dt
        new_position = pygame.math.Vector2(source_pos) - movement
        return new_position.x, new_position.y

    @staticmethod
    def rotate_towards(source_pos, target_pos):
        """
        Calculates the angle required to rotate from the source to the target.

        :param source_pos: The starting position (x, y) tuple.
        :param target_pos: The target position (x, y) tuple.
        :return: The angle in degrees to rotate towards the target.
        """
        difference = pygame.math.Vector2(target_pos) - pygame.math.Vector2(source_pos)
        angle = math.degrees(math.atan2(-difference.y, difference.x))
        return angle

    @staticmethod
    def keep_within_bounds(position, bounds):
        """
        Ensures that a position stays within specified bounds.

        :param position: The position (x, y) tuple to check.
        :param bounds: A tuple of the form (min_x, min_y, max_x, max_y) representing bounds.
        :return: The position clamped within the bounds.
        """
        x, y = position
        min_x, min_y, max_x, max_y = bounds
        clamped_x = max(min_x, min(x, max_x))
        clamped_y = max(min_y, min(y, max_y))
        return clamped_x, clamped_y

    @staticmethod
    def move_in_a_circle(center, radius, angle, angular_speed, dt):
        """
        Calculates the new position for an object moving in a circle.

        :param center: The center point of the circle (x, y).
        :param radius: The radius of the circle.
        :param angle: The current angle of the object in radians.
        :param angular_speed: The speed of rotation in radians per second.
        :param dt: The delta time (time since last frame) in seconds.
        :return: New (x, y) position and the updated angle.
        """
        new_angle = (angle + angular_speed * dt) % (2 * math.pi)
        x = center[0] + radius * math.cos(new_angle)
        y = center[1] + radius * math.sin(new_angle)
        return (x, y), new_angle

    @staticmethod
    def move_along_curve(start_pos, end_pos, control_point, t):
        """
        Moves an object from start_pos to end_pos along a quadratic Bézier curve defined by a control point.

        :param start_pos: The starting position (x, y) tuple.
        :param end_pos: The ending position (x, y) tuple.
        :param control_point: The control point (x, y) tuple that defines the curvature of the path.
        :param t: The interpolation factor (0.0 <= t <= 1.0) representing the object's position along the curve.
        :return: The new position (x, y) on the curve.
        """
        if not (0.0 <= t <= 1.0):
            raise ValueError("t must be between 0.0 and 1.0")
        x = (1 - t) ** 2 * start_pos[0] + 2 * (1 - t) * t * control_point[0] + t ** 2 * end_pos[0]
        y = (1 - t) ** 2 * start_pos[1] + 2 * (1 - t) * t * control_point[1] + t ** 2 * end_pos[1]
        return x, y

    @staticmethod
    def calculate_control_point(start_pos, end_pos, curve_height):
        """
        Calculates a control point for a quadratic Bézier curve to create a curved path between start and end points.

        :param start_pos: The starting position (x, y) tuple.
        :param end_pos: The ending position (x, y) tuple.
        :param curve_height: The height of the curve above the straight line connecting start and end points.
        :return: The control point (x, y) tuple.
        """
        mid_x = (start_pos[0] + end_pos[0]) / 2
        mid_y = (start_pos[1] + end_pos[1]) / 2
        control_x, control_y = mid_x, mid_y - curve_height
        return control_x, control_y

    @staticmethod
    def get_random_position_on_circle(start_pos, radius):
        """
        Generates a random position on a circle of a given radius around the start_pos.

        :param start_pos: The starting position (x, y) tuple.
        :param radius: The radius of the circle.
        :return: A tuple representing the random position (x, y) on the circle.
        """
        random_angle = random.uniform(0, 2 * math.pi)
        x = start_pos[0] + radius * math.cos(random_angle)
        y = start_pos[1] + radius * math.sin(random_angle)
        return x, y