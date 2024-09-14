import random
from enemies import CarnivorousPlantNPC
from npc import FallenStarNPC

def carnivorous_plants(game_manager):
    player_pos = game_manager.player.get_pos()
    plant_offsets = [(200, 200), (-200, 200), (200, -200), (-200, -200)]

    for offset in plant_offsets:
        plant_pos = (player_pos[0] + offset[0], player_pos[1] + offset[1])
        CarnivorousPlantNPC(plant_pos, game_manager.npcs_info['carnivorous_plant'], game_manager, game_manager.all_enemies)
    print("Triggered carnivorous_plants encounter")

def fallen_stars(game_manager):
    player_pos = game_manager.player.get_pos()
    offset_location = (player_pos[0] + random.randint(-500, 500), player_pos[1] + random.randint(-500, 500))
    fallen_star_npc = FallenStarNPC(offset_location, game_manager.npcs_info['fallen_star'], game_manager, game_manager.all_neutral_npcs)
    landing_location = (offset_location[0] + random.randint(-200, 200), offset_location[1] + random.randint(-200, 200))
    fallen_star_npc.set_target_pos(landing_location)
    print("Triggered fallen stars encounter")
