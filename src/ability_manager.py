import random
from ability import UpgradeType

class AbilityManager():
    def __init__(self, game_manager):
        self.game_manager = game_manager

    def get_upgrade_options(self):
        # Combine list construction and weight extraction
        upgrade_options = []
        upgrade_weights = []

        for ability in self.game_manager.player.abilities:
            for option in ability.upgrade_options:
                upgrade_options.append(option)
                upgrade_weights.append(option.rarity.weight)

        # Handle edge cases early
        if len(upgrade_options) < 3:
            raise ValueError("Not enough unique upgrade options available.")
        elif len(upgrade_options) == 3:
            return upgrade_options

        # Return a random weighted sample of 3 options
        return random.choices(upgrade_options, weights=upgrade_weights, k=3)
    
    def get_alteration_options(self):
        # Combine list construction and weight extraction
        alteration_options = []
        alteration_weights = []

        for ability in self.game_manager.player.abilities:
            for learnable_alteration in ability.learnable_alterations:
                alteration_options.append(learnable_alteration)
                alteration_weights.append(learnable_alteration.rarity.weight)

        # Handle edge cases early
        if len(alteration_options) < 3:
            raise ValueError("Not enough unique upgrade options available.")
        elif len(alteration_options) == 3:
            return alteration_options

        # Return a random weighted sample of 3 options
        return random.choices(alteration_options, weights=alteration_weights, k=3)

    def select_upgrade(self, option):
        for ability in self.game_manager.player.abilities:
            if option.type == UpgradeType.STAT_INCREASE:
                if ability.name == option.ability_name:
                    if hasattr(option, "stat"):
                        ability.upgrade_stat(option.stat, option.value)
                        return
            if option.type == UpgradeType.ALTERATION:
                ability.add_alteration(option)
                return