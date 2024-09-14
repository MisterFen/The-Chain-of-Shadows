import math
import pygame
import random
from boss_manager import BossFightManager
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_SPAWN_INTERVAL, MAX_ENEMY_COUNT, OFF_SCREEN_DISTANCE
from config.gamestates import GameState
from enemies import Enemy
from helpers import get_distance_between_points


class EnemyManager():
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.time_since_last_spawn_attempt = 0
        self.spawn_enemies(target=self.game_manager.player)
        self.boss_manager = BossFightManager(self.game_manager)

    def spawn_enemies(self, custom_spawn_pos = None, enemy_name=None, count=15, wave_pattern_id=None, target=None):
        spawn_pos = self.game_manager.player.get_pos()
        if custom_spawn_pos:
            spawn_pos = custom_spawn_pos
        self.check_for_far_away_enemies(spawn_pos)

        if len(self.game_manager.all_enemies) > MAX_ENEMY_COUNT:
            print("LOGGING: REACHED MAX ENEMY COUNT")
        else:
            self.game_manager.current_wave_number += 1
            self.all_spawnable_enemies = self.get_spawnable_enemies(self.game_manager.npcs_info)
            enemy_debug_name = enemy_name
            if enemy_debug_name == None:
                enemy_debug_name = random.choice(self.all_spawnable_enemies)
            # Create and add enemies to the game
            wave_type_id = wave_pattern_id
            if wave_type_id == None:
                wave_type_id = random.randint(0, 3)
            if wave_type_id == 0:
                self.spawn_line_enemies(spawn_pos, count, "vertical", self.game_manager, enemy_debug_name)
            elif wave_type_id == 1:
                self.spawn_line_enemies(spawn_pos, count, "horizontal", self.game_manager, enemy_debug_name)
            elif wave_type_id == 2:
                self.spawn_herd_enemies(spawn_pos, count, self.game_manager, enemy_debug_name)
            else:
                for _ in range(20):  # Example: spawn 5 enemies
                    enemy = Enemy((random.randint(spawn_pos[0]-SCREEN_WIDTH/2, spawn_pos[0]+SCREEN_WIDTH/2), random.randint(spawn_pos[1]-SCREEN_HEIGHT/2, spawn_pos[1]+SCREEN_HEIGHT/2)), self.game_manager.npcs_info[enemy_debug_name], self.game_manager, self.game_manager.all_enemies)
                    enemy.set_target(target)
        self.time_since_last_spawn_attempt = 0

    def check_for_far_away_enemies(self, player_pos):
        player_x, player_y = player_pos

        for enemy in self.game_manager.all_enemies:
            enemy_pos = enemy.get_pos()
            enemy_x, enemy_y = enemy_pos

            # Calculate the distance between the player and the enemy
            distance = get_distance_between_points(enemy.get_pos(), player_pos)

            if distance > SCREEN_WIDTH / 2 + 300: 
                # Calculate the inverse position relative to the player
                inverse_x = player_x + (player_x - enemy_x)
                inverse_y = player_y + (player_y - enemy_y)

                # Determine the new off-screen position
                if inverse_x > player_x:
                    new_enemy_x = player_x + SCREEN_WIDTH / 2 + OFF_SCREEN_DISTANCE
                else:
                    new_enemy_x = player_x - SCREEN_WIDTH / 2 - OFF_SCREEN_DISTANCE

                if inverse_y > player_y:
                    new_enemy_y = player_y + SCREEN_HEIGHT / 2 + OFF_SCREEN_DISTANCE
                else:
                    new_enemy_y = player_y - SCREEN_HEIGHT / 2 - OFF_SCREEN_DISTANCE

                # Set the new position of the enemy
                enemy.set_pos((new_enemy_x, new_enemy_y))

    def spawn_herd_enemies(self, player_pos, num_enemies, game_manager, debug_name, radius=100, random_offset=10, stagger=False):
        enemies = []
        center_x, center_y = player_pos

        for _ in range(num_enemies):
            # Randomly place enemies within the defined radius around the player
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(radius / 2, radius)
            x = center_x + distance * math.cos(angle) + random.randint(-random_offset, random_offset)
            y = center_y + distance * math.sin(angle) + random.randint(-random_offset, random_offset)

            # Ensure enemies are placed slightly offscreen, adjust the x and y accordingly
            if x < SCREEN_WIDTH / 2:
                x -= SCREEN_WIDTH / 2
            else:
                x += SCREEN_WIDTH / 2
            if y < SCREEN_HEIGHT / 2:
                y -= SCREEN_HEIGHT / 2
            else:
                y += SCREEN_HEIGHT / 2

            # Create the enemy and add it to the game manager
            enemy = Enemy((x, y), game_manager.npcs_info[debug_name], game_manager, game_manager.all_enemies)

            # Optionally set a staggered target
            if stagger:
                stagger_offset = random.uniform(0, 1)  # Random stagger delay
                enemy.set_target(self.game_manager.player, stagger_offset=stagger_offset)
            else:
                enemy.set_target(self.game_manager.player)

            enemies.append(enemy)

        return enemies
    def spawn_line_enemies(self, player_pos, num_enemies, direction, game_manager, debug_name, spacing=50, random_offset=30, stagger=False):
        # Calculate the total length of the line and offset to center the line on the player
        overall_length_of_line = num_enemies * spacing
        offset = -overall_length_of_line / 2

        for i in range(num_enemies):
            if direction == 'horizontal':
                # Vertical positions on left and right side
                y_left = player_pos[1] - SCREEN_HEIGHT / 2
                y_right = player_pos[1] + SCREEN_HEIGHT / 2
                x = player_pos[0] + i * spacing + offset
                
                # Adding randomness to position
                x += random.randint(-random_offset, random_offset)
                y_left += random.randint(-random_offset, random_offset)
                y_right += random.randint(-random_offset, random_offset)

                # Spawning enemies on the left and right sides
                left_enemy = Enemy((x, y_left), game_manager.npcs_info[debug_name], game_manager, game_manager.all_enemies)
                right_enemy = Enemy((x, y_right), game_manager.npcs_info[debug_name], game_manager, game_manager.all_enemies)

                # Optionally set a staggered target
                if stagger:
                    left_enemy.set_target(self.game_manager.player, stagger_offset=i)
                    right_enemy.set_target(self.game_manager.player, stagger_offset=i)
                else:
                    left_enemy.set_target(self.game_manager.player)
                    right_enemy.set_target(self.game_manager.player)

            elif direction == 'vertical':
                # Horizontal positions on top and bottom
                x_top = player_pos[0] - SCREEN_WIDTH / 2
                x_bottom = player_pos[0] + SCREEN_WIDTH / 2
                y = player_pos[1] + i * spacing + offset
                
                # Adding randomness to position
                x_top += random.randint(-random_offset, random_offset)
                x_bottom += random.randint(-random_offset, random_offset)
                y += random.randint(-random_offset, random_offset)

                # Spawning enemies on the top and bottom sides
                top_enemy = Enemy((x_top, y), game_manager.npcs_info[debug_name], game_manager, game_manager.all_enemies)
                bottom_enemy = Enemy((x_bottom, y), game_manager.npcs_info[debug_name], game_manager, game_manager.all_enemies)

                # Optionally set a staggered target
                if stagger:
                    top_enemy.set_target(self.game_manager.player, stagger_offset=i)
                    bottom_enemy.set_target(self.game_manager.player, stagger_offset=i)
                else:
                    top_enemy.set_target(self.game_manager.player)
                    bottom_enemy.set_target(self.game_manager.player)

    def get_spawnable_enemies(self, npc_info):
        spawnable_enemies = []
        for k, v in enumerate(npc_info):
            if 'event_only' not in npc_info[v].keys():
                spawnable_enemies.append(v)
        return spawnable_enemies
    
    def spawn_elite_enemy(self, pos):
        #TODO: Implement elite enemies
        debug_name = random.choice(self.all_spawnable_enemies)
        enemy = Enemy(pos, self.game_manager.npcs_info[debug_name], self.game_manager, self.game_manager.all_enemies)
        enemy.set_target(self.game_manager.player)
        self.game_manager.all_enemies.add(enemy)

    def update(self, dt):
        if self.game_manager.state == GameState.PLAYING:
            if self.game_manager.elapsed_time > self.game_manager.selected_stage['boss_spawn_timer']:
                self.start_boss_cutscene()
                return
            self.time_since_last_spawn_attempt += dt
            if self.time_since_last_spawn_attempt > ENEMY_SPAWN_INTERVAL:
                self.spawn_enemies(target=self.game_manager.player)
        if self.game_manager.state == GameState.BOSS_FIGHT:
            self.boss_manager.update(dt)

    def get_closest_enemy(self):
        closest_enemy = None
        min_distance = float('inf')
        for enemy in self.game_manager.all_enemies:
            distance = pygame.math.Vector2(self.game_manager.player.rect.center).distance_to(enemy.rect.center)
            if distance < min_distance:
                min_distance = distance
                closest_enemy = enemy
        return closest_enemy
    
    def get_random_enemy(self):
        random_enemy = None
        if len(self.game_manager.all_enemies) > 0:
            all_enemy_sprites = self.game_manager.all_enemies.sprites()
            random_enemy = random.choice(all_enemy_sprites)
        return random_enemy
    
    def start_boss_cutscene(self):
        self.game_manager.change_state(GameState.CUTSCENE)
        self.game_manager.all_enemies = pygame.sprite.Group()
        self.game_manager.cutscene_manager.start_cutscene()