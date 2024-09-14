import json
import random
from config.settings import BOSSES_INFO_PATH
from npc import NPC
from helpers import create_instance_of_ability

class BossFightManager:
    def __init__(self, game_manager):
        self.all_bosses_info = self.load_bosses_info()
        self.game_manager = game_manager
        self.current_boss = None
        self.boss_fight_active = False

    def start_boss_fight(self, boss_name):
        boss_info = self.get_boss_info(boss_name)
        self.current_boss = Boss(boss_info, self.game_manager, self.game_manager.all_enemies)
        self.boss_fight_active = True

    def update(self, dt):
        if self.boss_fight_active:
            self.current_boss.update(dt)
            self.spawn_boss_minions()
            if self.current_boss.is_defeated():
                self.end_boss_fight()

    def spawn_boss_minions(self):
        if self.current_boss.should_spawn_minions():
            enemy_type = self.current_boss.get_minion_type()
            self.game_manager.enemy_manager.spawn_special_wave(enemy_type)

    def end_boss_fight(self):
        self.boss_fight_active = False
        self.current_boss = None
        self.game_manager.advance_to_next_level()

    def load_bosses_info(self):
        bosses_info_file_path = BOSSES_INFO_PATH
        data = dict()
        with open(bosses_info_file_path, 'r') as file:
            data = json.load(file)
        return data

    def get_boss_info(self, boss_name):
        return self.all_bosses_info[boss_name]
        

class Boss(NPC):
    def __init__(self, boss_info, game_manager, *groups):
        self.game_manager = game_manager
        self.spawn_position = boss_info['spawn_position'][0] + game_manager.player.get_pos()[0], boss_info['spawn_position'][1] + game_manager.player.get_pos()[1]
        self.abilities = []
        
        super().__init__(self.spawn_position, boss_info, game_manager, *groups)
        self.populate_abilities()
        self.phase = 1

    def update(self, dt):
        super().update(dt)
        self.handle_abilities(dt)
        self.check_for_phase_change()

    def handle_abilities(self, dt):
        # Trigger boss abilities based on cooldown or condition
        for ability in self.abilities:
            ability.update(dt)
            if ability.can_trigger():
                ability.trigger()

    def check_for_phase_change(self):
        # Change phases based on health thresholds
        # if self.health < self.game_manager.get_phase_threshold(self.phase):
        #     self.phase += 1
        #     self.change_behavior_for_phase()
        pass

    def should_spawn_minions(self):
        # Determine if it's time to spawn minions
        return self.health < 50 and self.game_manager.enemy_manager.enemy_count() < 10

    def get_minion_type(self):
        # Return the type of minions to spawn
        return random.choice(self.minions)

    def is_defeated(self):
        return self.health <= 0

    def change_behavior_for_phase(self):
        # Change boss behavior when phases change
        pass
    
    def populate_abilities(self):
        for ability_name in self.starting_abilities:
            self.add_ability(ability_name)

    def add_ability(self, ability_name):
        ability_instance = create_instance_of_ability(ability_name, self.game_manager, self)
        self.abilities.append(ability_instance)

    def attack(self):
        """
        Performs an attack on the target if the enemy is allowed to attack (cooldown, etc.).
        """
        if self.can_attack():
            print(f"Enemy attacks {self.target}!")
            if hasattr(self.target, 'take_damage'):
                self.target.take_damage(self.damage)  # Inflicts damage on the target if applicable.
            self.time_since_last_attack = 0  # Resets attack cooldown timer.