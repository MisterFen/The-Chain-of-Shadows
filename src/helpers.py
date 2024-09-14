import abilities
import config.settings as settings
import json
import os
import pygame
from config.abilities_map import ability_map

def get_all_ability_projectile_classes() -> list:
    all_class_names = [cls.__name__ for cls in abilities.__dict__.values() if isinstance(cls, type) and issubclass(cls, abilities.AbilityCollisionSprite)]
    class_list = [getattr(abilities, name) for name in all_class_names]
    return class_list

def get_all_ability_classes() -> list:
    all_class_names = [cls.__name__ for cls in abilities.__dict__.values() if isinstance(cls, type) and issubclass(cls, abilities.Ability)]
    class_list = [getattr(abilities, name) for name in all_class_names]
    return class_list

def get_all_character_info() -> dict:
    character_file_path = settings.CHARACTER_INFO_PATH
    data = dict()
    with open(character_file_path, 'r') as file:
        data = json.load(file)
    return data['characters']

def get_all_abilities_info() -> dict:
    abilities_file_path = settings.ABILITY_INFO_PATH
    data = dict()
    with open(abilities_file_path, 'r') as file:
        data = json.load(file)
    return data

def get_all_items_info() -> dict:
    items_file_path = settings.ITEMS_INFO_PATH
    data = dict()
    with open(items_file_path, 'r') as file:
        data = json.load(file)
    return data

def get_all_stages_info() -> dict:
    stages_file_path = settings.STAGES_INFO_PATH
    data = dict()
    with open(stages_file_path, 'r') as file:
        data = json.load(file)
    return data['stages']

def create_instance_of_ability(ability_name, *args, **kwargs):
    if ability_name in ability_map:
        cls = ability_map[ability_name]
        return cls(*args, **kwargs)
    else:
        raise ValueError(f"Class '{ability_name}' not found in ability_map")
    
def load_animation_frames(path):
    frames = []
    all_frames = os.listdir(path)
    for frame_file in all_frames:
        frame = load_image(os.path.join(path, frame_file), convert_alpha=True)
        frames.append(frame)
    return frames

def get_debug_name_of_object(object_name):
    name = object_name.replace(" ", "_").lower()
    name = name.replace("'", "")
    return name

def get_all_npcs_info():
    npcs_file_path = settings.NPCS_INFO_PATH
    data = dict()
    with open(npcs_file_path, 'r') as file:
        data = json.load(file)
    return data

def load_image(
    image_path,
    scale_factor=None,
    desired_width=None,
    desired_height=None,
    use_transparency=True,  # Flag to determine if transparency should be used
    colorkey=None,  # Transparent color (only used if use_transparency is True)
    convert_alpha=True,
    flip_horizontally=False,
    flip_vertically=False,
    rotation_angle=0,
    custom_transparency=None
):
    """
    Load an image with various options such as scaling, transparency, rotation, and flipping.
    
    Args:
        path (str): The file path to the image.
        scale_factor (float, optional): A factor to scale the image. Overrides desired_width and desired_height if both are provided.
        desired_width (int, optional): The desired width of the image. Will be ignored if scale_factor is provided.
        desired_height (int, optional): The desired height of the image. Will be ignored if scale_factor is provided.
        use_transparency (bool, optional): Whether to use transparency or not.
        colorkey (tuple or None, optional): The color to be treated as transparent. If None and use_transparency is True, the top-left pixel color is used by default.
        convert_alpha (bool, optional): Whether to use convert_alpha() (with per-pixel transparency) or convert() (without per-pixel transparency).
        flip_horizontally (bool, optional): Whether to flip the image horizontally.
        flip_vertically (bool, optional): Whether to flip the image vertically.
        rotation_angle (float, optional): Angle to rotate the image in degrees.
        custom_transparency (int or None, optional): If set, will make the entire image this transparent (0 to 255).
        
    Returns:
        pygame.Surface: The processed image as a Pygame Surface.
    """
    if not os.path.exists(image_path):
        print(f"Path {image_path} cannot be found!")
        image = pygame.image.load(settings.DEFAULT_IMAGE_PATH)
        return
    else:
        # Load the image
        image = pygame.image.load(image_path)

    # Choose the correct conversion method
    if convert_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    # Scaling the image
    if scale_factor:
        width = int(image.get_width() * scale_factor)
        height = int(image.get_height() * scale_factor)
        image = pygame.transform.scale(image, (width, height))
    elif desired_width or desired_height:
        width = desired_width if desired_width else image.get_width()
        height = desired_height if desired_height else image.get_height()
        image = pygame.transform.scale(image, (width, height))

    # Apply flipping
    if flip_horizontally or flip_vertically:
        image = pygame.transform.flip(image, flip_horizontally, flip_vertically)

    # Apply rotation
    if rotation_angle:
        image = pygame.transform.rotate(image, rotation_angle)

    # Apply custom transparency
    if custom_transparency is not None:
        image.set_alpha(custom_transparency)

    # Set colorkey (transparency) if use_transparency is True
    if use_transparency:
        if colorkey is None:  # Default to the color of the top-left pixel
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)

    return image

def get_distance_between_points(start_pos, end_pos):
    """
    Calculates the Euclidean distance between two points.

    :param start_pos: The starting position (x, y) tuple.
    :param end_pos: The ending position (x, y) tuple.
    :return: The distance between the two points as a float.
    """
    return pygame.math.Vector2(start_pos).distance_to(end_pos)