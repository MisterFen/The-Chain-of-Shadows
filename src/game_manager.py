import pygame
import sys
from cinematic_manager import CinematicManager
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from config.gamestates import GameState
from cutscenes import CutsceneManager
from encounters.encounters import EncounterManager, Encounter
from enemy_manager import EnemyManager
from hud import HeaderBar
from menus import HomeScreen, StageSelectScreen, GameOverScreen, LevelUpScreen
from loot_manager import LootManager
from player import Player
from quadtree import QuadTree
from stages import Stage
from sound_manager import SoundManager
from ui_manager import UIManager
import helpers
import cProfile

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Chain of Shadows")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.HOME_SCREEN

        # Initialize game objects
        self.all_map_sprites = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_neutral_npcs = pygame.sprite.Group()
        self.all_enemies = pygame.sprite.Group()
        self.all_ability_sprites = pygame.sprite.Group()
        self.in_game_ui = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.hud_elements = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.Group()
        self.damage_texts = pygame.sprite.Group()  # Group for damage texts

        # Loaded data from files
        self.ability_info = helpers.get_all_abilities_info()
        self.character_info = helpers.get_all_character_info()
        self.items_info = helpers.get_all_items_info()
        self.npcs_info = helpers.get_all_npcs_info()
        self.stages_info = helpers.get_all_stages_info()
        
        # Global Managers
        self.cinematic_manager = CinematicManager(self)
        self.cutscene_manager = CutsceneManager(self)
        self.sound_manager = SoundManager()
        self.ui_manager = UIManager(self)

        # Game stats
        self.selected_stage = self.stages_info[0]
        self.selected_character = [x for x in self.character_info if x['name'] == self.selected_stage['playable_character']][0]
        self.current_wave_number = 0
        self.enemies_defeated = 0

        # Screens
        self.home_screen = HomeScreen(self)
        self.stage_select_screen = StageSelectScreen(self, self.stages_info)
        self.game_over_screen = GameOverScreen(self)
        self.level_up_screen = LevelUpScreen(self)

        self.cutscene = None

        self.sound_manager.play_music(self.home_screen.music_track_path)

    def change_state(self, new_state):
        self.state = new_state

    def load_assets(self):
        # Load images, sounds, etc.
        pass

    def new_game(self):
        # Load assets and initialize other elements
        self.load_assets()

        self.camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        # Start a new game
        self.all_sprites.empty()
        self.all_map_sprites.empty()
        self.all_enemies.empty()
        self.in_game_ui.empty()
        self.hud_elements.empty()
        self.items.empty()
        self.player_sprites.empty()

        self.current_wave_number = 0
        self.enemies_defeated = 0
        self.elapsed_time = 0

        # Initialize player, enemies, and items
        self.player = Player((100, 100), self)
        self.enemy_manager = EnemyManager(self)
        self.header_bar = HeaderBar(self, self.hud_elements)
        self.loot_manager = LootManager(self)
        self.encounter_manager = EncounterManager(self, min_distance=self.stage.random_encounter_distance)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000  # Convert milliseconds to seconds
            if self.state == GameState.HOME_SCREEN:
                self.home_screen.handle_events(pygame.event.get())
                self.home_screen.display()
            elif self.state == GameState.STAGE_SELECT:
                self.stage_select_screen.handle_events(pygame.event.get())
                self.stage_select_screen.display()
            elif self.state == GameState.CINEMATIC:
                self.sound_manager.load_stage(self.stage)
                self.cinematic_manager.play_cinematic(self.stage.name.lower()+"_intro")  # Play intro cinematic
            elif self.state == GameState.NEW_GAME:
                self.new_game()
                self.change_state(GameState.PLAYING)
            elif self.state == GameState.GAME_OVER:
                self.game_over_screen.handle_events(pygame.event.get())
                self.draw(self.game_over_screen)
            elif self.state == GameState.PLAYING:
                self.elapsed_time += dt
                self.handle_events()
                self.update(dt)
                self.draw()
            elif self.state == GameState.CUTSCENE:
                self.cutscene_manager.update(dt)
                self.draw()
            elif self.state == GameState.LEVEL_UP:
                self.level_up_screen.handle_events(pygame.event.get())
                self.draw(self.level_up_screen)
            elif self.state == GameState.BOSS_FIGHT:
                self.elapsed_time += dt
                self.handle_events()
                self.update(dt)
                self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # Handle other key events, such as pause, restart, etc.

    def update(self, dt):
        self.enemy_manager.update(dt)
        # Update all sprites

        self.all_sprites.update(dt)
        self.all_ability_sprites.update(dt)  # Update abilities
        self.all_enemies.update(dt)
        self.all_map_sprites.update(dt)
        self.all_neutral_npcs.update(dt)
        self.player_sprites.update(dt)
        
        # Update camera position to follow player
        self.camera.center = self.player.rect.center
        self.encounter_manager.update()
        self.hud_elements.update()
        self.in_game_ui.update(self.camera.topleft)
        self.ui_manager.update(dt)

        # Check collisions
        self.check_collisions()

    def draw(self, overlay_screen=None):
        # Clear screen
        self.screen.fill((30, 30, 30))

        # Draw all sprites with camera adjustment
        self.stage.draw()
        for map_item in self.items:
            screen_pos = map_item.rect.move(-self.camera.topleft[0], -self.camera.topleft[1])
            self.screen.blit(map_item.image, screen_pos)
        for item in self.items:
            screen_pos = item.rect.move(-self.camera.topleft[0], -self.camera.topleft[1])
            self.screen.blit(item.image, screen_pos)
        for sprite in self.all_sprites:
            screen_pos = sprite.rect.move(-self.camera.topleft[0], -self.camera.topleft[1])
            self.screen.blit(sprite.image, screen_pos)
        for enemy_sprite in self.all_enemies:
            enemy_sprite.draw(self.screen)
        for neutral_npc in self.all_neutral_npcs:
            neutral_npc.draw(self.screen)
        for ability_sprite in self.all_ability_sprites:
            ability_sprite.draw(self.screen)
        for player_sprite in self.player_sprites:
            screen_pos = player_sprite.rect.move(-self.camera.topleft[0], -self.camera.topleft[1])
            self.screen.blit(player_sprite.image, screen_pos)
        self.in_game_ui.draw(self.screen)
        self.hud_elements.draw(self.screen)
        self.ui_manager.draw(self.screen)
        if overlay_screen:
            overlay_screen.display()
       
        # Update display
        pygame.display.flip()

    def check_collisions(self):
        world_boundary = pygame.Rect(self.player.rect.centerx-SCREEN_WIDTH/2, self.player.rect.centery-SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT)
        quadtree = QuadTree(world_boundary, 4)  # capacity = 4 objects per node
        for enemy in self.all_enemies:
            quadtree.insert(enemy)
        nearby_enemies = quadtree.query(self.player.rect, [])
        # Check collisions between player and enemies
        player_hits = pygame.sprite.spritecollide(self.player, nearby_enemies, False, pygame.sprite.collide_rect)
        for enemy in player_hits:
            enemy.attack()

        item_hits = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in item_hits:
            item.on_collect()