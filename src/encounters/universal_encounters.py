import random
from npc import TemporalRiftNPC

def temporal_rift(game_manager):
    player_pos = game_manager.player.get_pos()
    offset_location = (player_pos[0] + random.randint(-500, 500), player_pos[1] + random.randint(-500, 500))
    TemporalRiftNPC(offset_location, game_manager.npcs_info['temporal_rift'], game_manager, game_manager.all_neutral_npcs)
    print("Triggered Temporal Rift!")