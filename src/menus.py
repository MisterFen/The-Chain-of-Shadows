import os
import pygame
import sys
from config.settings import ABILITIES_IMAGES_ROOT_PATH, BACKGROUND_IMAGE_PATH, BUTTON_IMAGE_PATH, HEROES_IMAGE_ROOT, SOUNDS_ROOT_PATH
from config.gamestates import GameState
from animated_sprite import AnimatedSprite
from stages import Stage
import helpers

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Button:
    def __init__(self, image, pos, text, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text = text
        self.text_render = self.font.render(self.text, True, self.base_color)
        if self.image is None:
            self.image = self.text_render
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text_render.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        screen.blit(self.text_render, self.text_rect)

    def check_for_input(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def change_color(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text_render = self.font.render(self.text, True, self.hovering_color)
        else:
            self.text_render = self.font.render(self.text, True, self.base_color)

class Menu:
    def __init__(self, screen, background_image, buttons, display_elements=None):
        self.screen = screen
        self.background_image = background_image
        self.buttons = buttons
        self.display_elements = display_elements

    def display(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for button in self.buttons:
            button.change_color(mouse_pos)
            button.update(self.screen)
        
        if self.display_elements:
            for display_element in self.display_elements:
                display_element.update(self.screen)

        pygame.display.update()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.check_for_input(mouse_pos):
                        return button.text
        return None

class HomeScreen(Menu):
    def __init__(self, game_manager):
        background_image = helpers.load_image(BACKGROUND_IMAGE_PATH)
        button_image = helpers.load_image(BUTTON_IMAGE_PATH, convert_alpha=True)
        font = pygame.font.SysFont("Arial", 36)
        # Define buttons for the home screen
        buttons = [
            Button(image=button_image, pos=(400, 300), text="Play", font=font, base_color=WHITE, hovering_color=BLACK),
            Button(image=button_image, pos=(400, 400), text="Quit", font=font, base_color=WHITE, hovering_color=BLACK)
        ]

        super().__init__(game_manager.screen, background_image, buttons)
        self.game_manager = game_manager
        self.music_track_path = os.path.join(SOUNDS_ROOT_PATH, "music", "main_menu.mp3")

    def handle_events(self, events):
        button_text = super().handle_events(events)
        if button_text == "Play":
            self.game_manager.change_state(GameState.STAGE_SELECT)
        elif button_text == "Quit":
            self.game_manager.running = False

class StageButton(Button):
    def __init__(self, image, pos, text, font, base_color, hovering_color):
        super().__init__(image, pos, text, font, base_color, hovering_color)

class PictureFrame:
    def __init__(self, game_manager, pos, size):
        self.game_manager = game_manager
        self.x_pos, self.y_pos = pos
        self.width, self.height = size
        self.set_animation_frames()
        self.image = self.animation_frames[0]
        self.rect = pygame.Rect(self.x_pos, self.y_pos, self.width, self.height)

    def set_animation_frames(self):
        character_name = helpers.get_debug_name_of_object(self.game_manager.selected_character['name'])
        self.animation_frames = helpers.load_animation_frames(os.path.join(HEROES_IMAGE_ROOT, character_name, "in_game"))
        self.animation = AnimatedSprite(self.animation_frames, self.x_pos, self.y_pos, 300)

    def update(self, screen):
        self.animation.update()
        self.image = self.animation.image
        scaled_image = pygame.transform.scale(self.image, (self.width, self.height))
        screen.blit(scaled_image, self.rect)

class StageSelectScreen(Menu):
    def __init__(self, game_manager, stages):
        background_image = helpers.load_image(BACKGROUND_IMAGE_PATH, convert_alpha=True)
        button_image = helpers.load_image(BUTTON_IMAGE_PATH, convert_alpha=True)
        font = pygame.font.SysFont("Arial", 36)

        # Create buttons for each character
        buttons = []
        for idx, stage in enumerate(stages):
            button = StageButton(
                image=button_image,
                pos=(400, 200 + idx * 100),  # Adjust positions as needed
                text=stage["name"],
                font=font,
                base_color=WHITE,
                hovering_color=BLACK
            )
            buttons.append(button)
        continue_button = Button(image=button_image, pos=(1500, 900), text="Start", font=font, base_color=WHITE, hovering_color=BLACK)
        buttons.append(continue_button)
        self.game_manager = game_manager
        self.stages = stages
        self.picture_frame = PictureFrame(self.game_manager, pos=(1100, 200), size=(300, 300))
        super().__init__(game_manager.screen, background_image, buttons, display_elements=[self.picture_frame])

    def display(self):
        self.picture_frame.update(self.screen)
        super().display()

    def handle_events(self, events):
        button_text = super().handle_events(events)
        if button_text:
            # Find the selected character
            selected_stage = next((stage for stage in self.stages if stage["name"] == button_text), None)
            if selected_stage:
                self.game_manager.selected_stage = selected_stage
                self.game_manager.selected_character = [x for x in self.game_manager.character_info if x['name'] == self.game_manager.selected_stage['playable_character']][0]
                self.picture_frame.set_animation_frames()
            if button_text == "Start":
                self.game_manager.change_state(GameState.CINEMATIC)
                self.game_manager.stage = Stage(self.game_manager)

class GameOverScreen(Menu):
    def __init__(self, game_manager):
        self.game_manager = game_manager
        button_image = helpers.load_image(BUTTON_IMAGE_PATH, convert_alpha=True)
        font = pygame.font.SysFont("Arial", 36)
        self.overlay = pygame.Surface(self.game_manager.screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # Increase alpha to make the overlay more translucent
        # Define buttons for the game over screen
        self.buttons = [
            Button(image=button_image, pos=(400, 300), text="Restart", font=font, base_color=WHITE, hovering_color=BLACK),
            Button(image=button_image, pos=(400, 400), text="Quit", font=font, base_color=WHITE, hovering_color=BLACK)
        ]

    def display(self):
        # Draw a translucent overlay
        self.game_manager.screen.blit(self.overlay, (0, 0))

        # Draw the buttons
        mouse_pos = pygame.mouse.get_pos()

        for button in self.buttons:
            button.change_color(mouse_pos)
            button.update(self.game_manager.screen)

        pygame.display.update()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.check_for_input(mouse_pos):
                        if button.text == "Restart":
                            self.game_manager.change_state(GameState.PLAYING)
                            self.game_manager.new_game()  # Restart the game
                        elif button.text == "Quit":
                            self.game_manager.change_state(GameState.HOME_SCREEN)

class UpgradeOptionDisplay:
    def __init__(self, image, pos, ability_name, description, rarity, font, button, upgrade_option, max_width=300):
        self.image = image
        self.x_pos, self.y_pos = pos
        self.ability_name = ability_name
        self.description = description
        self.font = font
        self.max_width = max_width
        self.rarity = rarity
        self.upgrade_option = upgrade_option

        # Position the image
        self.image_rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

        # Wrap the description text and position it
        self.text_lines = self.wrap_text(self.description)
        self.text_renders = [self.font.render(line, True, WHITE) for line in self.text_lines]
        self.text_rects = [render.get_rect(midleft=(self.x_pos + 100, self.y_pos + i * render.get_height())) for i, render in enumerate(self.text_renders)]
        
        # Create the button, adjusting its position to avoid overlap with the text
        self.button = Button(image=button.image, 
                             pos=(self.x_pos + 100, self.y_pos + len(self.text_lines) * self.font.get_height() + 10), 
                             text=button.text, 
                             font=button.font, 
                             base_color=button.base_color, 
                             hovering_color=button.hovering_color)

    def wrap_text(self, text):
        """Splits the text into lines so that it fits within the max width."""
        words = text.split(' ')
        lines = []
        current_line = words[0]

        for word in words[1:]:
            # Check if adding the next word exceeds the max width
            if self.font.size(current_line + ' ' + word)[0] <= self.max_width:
                current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)  # Add the last line
        return lines

    def update(self, screen):
        screen.blit(self.image, self.image_rect)
        for render, rect in zip(self.text_renders, self.text_rects):
            screen.blit(render, rect)
        self.button.update(screen)

    def check_for_input(self, position):
        return self.button.check_for_input(position)

class LevelUpScreen(Menu):
    def __init__(self, game_manager):
        screen_size = game_manager.screen.get_size()
        box_width, box_height = 800, 400  # Size of the level-up box
        self.box_x = (screen_size[0] - box_width) // 2
        self.box_y = (screen_size[1] - box_height) // 2

        # Create a translucent overlay to dim the game screen
        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # Translucent black

        # Create the level-up box
        self.box_rect = pygame.Rect(self.box_x, self.box_y, box_width, box_height)
        self.box_surface = pygame.Surface((box_width, box_height))
        self.box_surface.fill((50, 50, 50))  # Dark grey background

        # Font for the text
        self.font = pygame.font.SysFont("Arial", 12)

        # Create buttons and upgrade options within the box
        self.upgrade_option_displays = []

        self.game_manager = game_manager

    def set_upgrade_options(self, upgrade_options):
        self.upgrade_option_displays = []
        for idx, option in enumerate(upgrade_options):
            button = Button(image=None, pos=(self.box_x + 600, self.box_y + 50 + idx * 100), text="Choose", font=self.font, base_color=WHITE, hovering_color=BLACK)

            name = "DEFAULT. CHANGE ME"
            if hasattr(option, "name"):
                name = option.name
            if hasattr(option, "ability_name"):
                name = option.ability_name

            upgrade_option_display = UpgradeOptionDisplay(
                image=helpers.load_image(os.path.join(ABILITIES_IMAGES_ROOT_PATH, helpers.get_debug_name_of_object(name), "icon", "frame_0.png")),
                pos=(self.box_x + 100, self.box_y + 50 + idx * 100),
                ability_name=name,
                description=option.description,
                rarity=option.rarity,
                font=self.font,
                button=button,
                upgrade_option=option
            )
            self.upgrade_option_displays.append(upgrade_option_display)

        super().__init__(self.game_manager.screen, None, buttons=[opt.button for opt in self.upgrade_option_displays])

    def display(self):
        # Draw the translucent overlay
        self.screen.blit(self.overlay, (0, 0))

        # Draw the level-up box
        self.screen.blit(self.box_surface, self.box_rect.topleft)

        # Update and display each upgrade option within the box
        mouse_pos = pygame.mouse.get_pos()
        for option in self.upgrade_option_displays:
            option.button.change_color(mouse_pos)
            option.update(self.screen)

        pygame.display.update()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for option_display in self.upgrade_option_displays:
                    if option_display.check_for_input(mouse_pos):
                        self.game_manager.player.ability_manager.select_upgrade(option_display.upgrade_option)
                        if self.game_manager.enemy_manager.boss_manager.boss_fight_active:
                            self.game_manager.change_state(GameState.BOSS_FIGHT)
                            return True
                        self.game_manager.change_state(GameState.PLAYING)
        return None