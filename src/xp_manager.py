from config.gamestates import GameState

class XPManager:
    def __init__(self, game_manager, initial_xp=0, xp_per_level=10):
        self.game_manager = game_manager
        self.current_xp = initial_xp
        self.xp_per_level = xp_per_level
        self.level = 1

    def gain_xp(self, amount):
        """Add XP to the current total and handle level-ups."""
        self.current_xp += amount
        while self.current_xp >= self.xp_per_level:
            self.level_up()

    def level_up(self):
        """Increase the player's level and adjust XP accordingly."""
        self.level += 1
        self.current_xp -= self.xp_per_level
        print(f"Level up! You are now level {self.level}")

        # Increase XP required for next level by 10%
        self.xp_per_level = int(self.xp_per_level * 1.1)

        # Handle game state changes and upgrades
        self.game_manager.change_state(GameState.LEVEL_UP)
        upgrade_options = self.game_manager.player.ability_manager.get_upgrade_options()

        # Every 10 levels, offer alterations instead of regular upgrades
        if self.level % 10 == 0:
            upgrade_options = self.game_manager.player.ability_manager.get_alteration_options()

        self.game_manager.level_up_screen.set_upgrade_options(upgrade_options)

    def get_xp_for_next_level(self):
        """Return the XP required to reach the next level."""
        return self.xp_per_level - self.current_xp

    def set_xp_per_level(self, new_xp_per_level):
        """Adjust the XP required per level. Useful if XP requirements increase with each level."""
        self.xp_per_level = new_xp_per_level

    def reset(self):
        """Reset XP and level to initial values."""
        self.current_xp = 0
        self.level = 1
        self.xp_per_level = 10  # Reset xp_per_level to the starting value