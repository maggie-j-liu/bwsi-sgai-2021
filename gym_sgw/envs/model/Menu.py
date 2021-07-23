import pygame as pg
import pygame.display
from gym_sgw.envs.enums.Enums import GameState
from gym_sgw.envs.model.UIElement import UIElement
from pygame.sprite import RenderUpdates


class Menu:

    def __init__(self):
        pg.init()
        self.screen = pygame.display.set_mode((1000, 800))
        self.bg_color = (106, 159, 181)  # placeholder color value rn (R, G, B)
        self.text_color = ()
        self.game_state = None

    def load_menu(self, game_state):
        print("in load_menu")
        self.game_state = game_state
        print(self.game_state)

        while True:
            # runs start screen if game state is title
            if game_state == GameState.title:
                print("game state is title")
                game_state = self.start_screen(self.screen)

            # returns the game state back to where menu is called (sgwhumanplay) so real game can start
            if game_state == GameState.new_game:
                print("game state is new game")
                game_state == self.play_level()
                return game_state

            # runs end screen if game state is close
            if game_state == GameState.close:
                print("game state is close")
                game_state == self.end_screen(self.screen)

            # quits game if game state is quit
            if game_state == GameState.quit:
                print("game state is quit")
                pg.quit()
                return

    def start_screen(self, screen):
        print("in start_screen")
        start_btn = UIElement(
            center_pos=(400, 400),
            font_size=30,
            bg_rgb=None,
            text_rgb=None,
            text="Start",
            action=GameState.new_game
        )
        quit_btn = UIElement(
            center_pos=(400, 500),
            font_size=30,
            bg_rgb=None,
            text_rgb=None,
            text="Quit",
            action=GameState.quit
        )

        buttons = RenderUpdates(start_btn, quit_btn)

        return self.menu_loop(self.screen, buttons)

    def play_level(self):
        if self.game_state == GameState.new_game:
            return True
        else:
            return False

    def end_screen(self, screen):
        replay_btn = UIElement(
            center_pos=None,
            font_size=None,
            bg_rgb=None,
            text_rgb=None,
            text="Replay",
            action=GameState.new_game
        )
        quit_btn = UIElement(
            center_pos=None,
            font_size=None,
            bg_rgb=None,
            text_rgb=None,
            text="Quit",
            action=GameState.quit
        )

        buttons = RenderUpdates(replay_btn, quit_btn)

        return self.menu_loop(self.screen, buttons)

    # loop until an action is returned by a button in the button sprites renderer
    def menu_loop(self, screen, buttons):
        print("in menu_loop")
        while True:
            mouse_up = False
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_up = True
            screen.fill(self.bg_color)  # color (R, G, B)

            for button in buttons:
                ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
                if ui_action is not None:
                    print("ui_action: ", ui_action)
                    return ui_action

            buttons.draw(screen)
            pygame.display.flip()



