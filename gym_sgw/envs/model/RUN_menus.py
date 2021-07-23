from gym_sgw.envs.model.Menu import Menu
from gym_sgw.envs.enums.Enums import GameState

"""
this is a literally a file just to run the menus for testing/debugging purposes!! 
run this file by itself just for menu stuff. not actually called in any part of the game 
"""


class RUN_menus:

    def __init__(self):
        print("in init")
        self.menu = Menu()
        self.start = None
        self.game_state = GameState.title

    def start_menu(self):
        print("in start_menu")
        self.start = self.menu.load_menu(game_state=self.game_state)


menu = RUN_menus()
menu.start_menu()
