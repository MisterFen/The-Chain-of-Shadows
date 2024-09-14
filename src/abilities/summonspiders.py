from ability import Ability

class SummonSpiders(Ability):
    def __init__(self, game_manager, ability_owner):
        self.debug_name = "summon_spiders"
        self.ability_info = game_manager.ability_info[self.debug_name]
        super().__init__(self.ability_info, game_manager, ability_owner)

    def trigger(self):
        self.spawn_spiders()
        self.time_since_last_use = 0

    def spawn_spiders(self):
        spawn_pos = self.ability_owner.get_pos()
        self.game_manager.enemy_manager.spawn_enemies(spawn_pos, enemy_name="acromantula", count=15, wave_pattern_id=66, target=self.game_manager.player)