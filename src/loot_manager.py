from enum import Enum
from items import Collectible, XPItem, HealingItem
import random

class ItemTypes(Enum):
    HEALING = "healing"
    XP = "xp"
    COLLECTIBLE = "collectible"

class LootManager():
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.items_info = self.game_manager.items_info

    def spawn_random_drop(self, loot_list, spawn_pos):
        random_item = random.choice(loot_list)
        item_data = self.items_info[random_item]
        if item_data['type'] == ItemTypes.XP.value:
            return XPItem(self.game_manager, item_data['id'], item_data['name'], item_data['description'],
                item_data['xp_value'], item_data['score'], spawn_pos, self.game_manager.items
            )
        
    def spawn_event_item(self, item_type, spawn_pos):
        if item_type == ItemTypes.XP:
            item_data = self.items_info['large_xp_orb']
            return XPItem(self.game_manager, item_data['id'], item_data['name'], item_data['description'],
                item_data['xp_value'], item_data['score'], spawn_pos, self.game_manager.items
            )