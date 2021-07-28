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
        self.stats = {}

    def load_menu(self, game_state, stats=None):
        
        print("in load_menu ", game_state)
        self.game_state = game_state

        if stats is not None:
            self.stats = stats

        while True:
            # runs start screen if game state is title
            if self.game_state == GameState.title:
                # print("game state is title")
                self.game_state = self.start_screen(self.screen)

            # returns the game state back to where menu is called (sgwhumanplay) so real game can start
            if self.game_state == GameState.new_human_game or self.game_state == GameState.new_machine_game:
                print("game state is new game")
                #self.game_state = self.play_level()
                return self.game_state

            # runs end screen if game state is close
            if self.game_state == GameState.close:
                # print("game state is close")
                self.game_state = self.end_screen(self.screen)

            # quits game if game state is quit
            if self.game_state == GameState.quit:
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
            center_pos=(250, 330),
            font_size=30,
            bg_rgb=SchemeColors.light_pink.value,
            high_bg_rgb=SchemeColors.pink.value,
            text_rgb=None,
            text="Options"
        )
        quit_btn = UIElement(
            center_pos=(295, 370),
            font_size=30,
            bg_rgb=SchemeColors.light_orange.value,
            high_bg_rgb=SchemeColors.orange.value,
            text_rgb=None,
            text="Quit (Esc)",
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
            desc_font = pygame.freetype.SysFont("Calibri", 30, italic=True)
            num_font = pygame.freetype.SysFont("Calibri", 40, bold=True)
            desc_font.render_to(surface, (100, 100), "You achieved a score of : ", (0, 0, 0))
            num_font.render_to(surface, (500, 100), str(self.stats['score']), SchemeColors.orange.value)
            desc_font.render_to(surface, (100, 150), "Number of turns: ", SchemeColors.light_purple.value)
            num_font.render_to(surface, (500, 150), str(self.stats['turns_executed']), SchemeColors.purple.value)
            desc_font.render_to(surface, (100, 180), "Percent of injured saved: ", SchemeColors.light_pink.value)
            num_font.render_to(surface, (500, 180), str(self.stats['percent_saved']), SchemeColors.pink.value)

    def play_level(self):
        if self.game_state == GameState.new_human_game or self.game_state == GameState.new_machine_game:
            return True
        else:
            return False

    def end_screen(self, screen):
        # menu button doesn't work :(

        # menu_btn = UIElement(
        #     center_pos=(450, 500),
        #     font_size=30,
        #     bg_rgb=SchemeColors.blue.value,
        #     high_bg_rgb=SchemeColors.light_blue.value,
        #     text_rgb=SchemeColors.white.value,
        #     text="Menu",
        #     action=None
        # )

        quit_btn = UIElement(
            center_pos=(500, 590),
            font_size=55,
            bg_rgb=SchemeColors.orange.value,
            high_bg_rgb=SchemeColors.light_orange.value,
            text_rgb=SchemeColors.white.value,
            text="Quit",
            action=GameState.quit
        )

        buttons = RenderUpdates(quit_btn)

        return self.menu_loop(screen, buttons)

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
                    self.game_state = ui_action
                    return ui_action
            # update screen
            buttons.draw(screen)
            pygame.display.flip()



