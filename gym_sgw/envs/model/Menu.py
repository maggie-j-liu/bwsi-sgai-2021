import pygame as pg
import pygame.display
import pygame.freetype
from gym_sgw.envs.enums.Enums import GameState, SchemeColors
from gym_sgw.envs.model.UIElement import UIElement
from pygame.sprite import RenderUpdates


class Menu:

    def __init__(self):
        pg.init()
        self.screen = pygame.display.set_mode((1000, 800))
        self.bg_color = SchemeColors.white.value
        self.text_color = ()
        self.game_state = None

    def load_menu(self, game_state):
        
        # print("in load_menu")
        self.game_state = game_state
        # print(self.game_state)

        while True:
            # runs start screen if game state is title
            if game_state == GameState.title:
                # print("game state is title")
                game_state = self.start_screen(self.screen)
                self.game_state = game_state

            # returns the game state back to where menu is called (sgwhumanplay) so real game can start
            if game_state == GameState.new_human_game or game_state == GameState.new_machine_game:
                # print("game state is new game")
                game_state == self.play_level()
                self.game_state = game_state
                return game_state

            # runs end screen if game state is close
            if game_state == GameState.close:
                # print("game state is close")
                game_state == self.end_screen(self.screen)

            # quits game if game state is quit
            if game_state == GameState.quit:
                # print("game state is quit")
                self.game_state = game_state
                pg.quit()
                return

    def start_screen(self, screen):
        # print("in start_screen")
        human_start_btn = UIElement(
            center_pos=(200, 250),
            font_size=30,
            bg_rgb=SchemeColors.light_blue.value,
            high_bg_rgb=SchemeColors.blue.value,
            text_rgb=None,
            text="Human Play",
            action=GameState.new_human_game
        )
        machine_start_btn = UIElement(
            center_pos=(250, 290),
            font_size=30,
            bg_rgb=SchemeColors.light_purple.value,
            high_bg_rgb=SchemeColors.purple.value,
            text_rgb=None,
            text="Automatic Play",
            action=GameState.new_machine_game
        )
        options_btn = UIElement(
            center_pos=(255, 330),
            font_size=30,
            bg_rgb=SchemeColors.light_pink.value,
            high_bg_rgb=SchemeColors.pink.value,
            text_rgb=None,
            text="Options"
        )
        quit_btn = UIElement(
            center_pos=(290, 370),
            font_size=30,
            bg_rgb=SchemeColors.light_orange.value,
            high_bg_rgb=SchemeColors.orange.value,
            text_rgb=None,
            text="Quit",
            action=GameState.quit
        )

        buttons = RenderUpdates(human_start_btn, machine_start_btn, options_btn, quit_btn)

        return self.menu_loop(self.screen, buttons)

    # draw shapes/text stuff that aren't buttons onto screen window
    def draw_shapes(self, screen):
        surface = screen
        if self.game_state == GameState.title:
            # buttons style rectangle things
            pygame.draw.rect(surface, SchemeColors.light_blue.value, pygame.Rect(0, 234, 1000, 32))
            pygame.draw.rect(surface, SchemeColors.light_purple.value, pygame.Rect(0, 274, 1000, 32))
            pygame.draw.rect(surface, SchemeColors.light_pink.value, pygame.Rect(0, 314, 1000, 32))
            pygame.draw.rect(surface, SchemeColors.light_orange.value, pygame.Rect(0, 354, 1000, 32))
            # add title
            title_font = pygame.freetype.SysFont("Calibri", 70, bold=True)
            title_font.render_to(surface, (190, 90), "Wildfire Rescue", (0, 0, 0))

        elif self.game_state == GameState.close:
            pass

    def play_level(self):
        if self.game_state == GameState.new_human_game or self.game_state == GameState.new_machine_game:
            return True
        else:
            return False

    def end_screen(self, screen):
        replay_btn = UIElement(
            center_pos=(450, 500),
            font_size=30,
            bg_rgb=SchemeColors.blue.value,
            text_rgb=SchemeColors.white.value,
            text="Replay",
            action=self.game_state
        )
        quit_btn = UIElement(
            center_pos=(550, 500),
            font_size=30,
            bg_rgb=SchemeColors.orange.value,
            text_rgb=SchemeColors.white.value,
            text="Quit",
            action=GameState.quit
        )

        buttons = RenderUpdates(replay_btn, quit_btn)

        return self.menu_loop(self.screen, buttons)

    # loop until an action is returned by a button in the button sprites renderer
    def menu_loop(self, screen, buttons):
        # print("in menu_loop")
        while True:
            mouse_up = False
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_up = True
            screen.fill(self.bg_color)  # color (R, G, B)
            self.draw_shapes(screen)

            for button in buttons:
                ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
                if ui_action is not None:
                    # print("ui_action: ", ui_action)
                    return ui_action

            buttons.draw(screen)
            pygame.display.flip()



