import json
import uuid
import gym
import gym_sgw  # Required, don't remove!
import pygame as pg
from gym_sgw.envs.enums.Enums import Actions, Terrains, PlayTypes, MapProfiles, MapColors
from choose_action import choose_action


class SGW:
    """
    Machine play game variant using a pathfinding algorithm.
    """
    def __init__(self, data_log_file='data_log.json', max_energy=50, map_file=None,
                 rand_prof=MapProfiles.trolley, num_rows=25, num_cols=25, manual=False):
        self.ENV_NAME = 'SGW-v0'
        self.DATA_LOG_FILE_NAME = data_log_file
        self.GAME_ID = uuid.uuid4()
        self.env = None
        self.current_action = Actions.none
        self.max_energy = max_energy
        self.map_file = map_file
        self.rand_prof = rand_prof
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.is_game_over = False
        self.turn = 0
        self.max_turn = 300  # to prevent endless loops and games
        self.cell_size = 30
        self.game_screen = None
        self.play_area = None
        self.latest_obs = None
        self.manual = manual

        # Always do these actions upon start
        self._setup()

    def _setup(self):
        # Game parameters
        self.env = gym.make(self.ENV_NAME)
        self.env.play_type = PlayTypes.machine  # We will get human states and observations back
        self.env.max_energy = self.max_energy
        self.env.map_file = self.map_file
        self.env.rand_profile = self.rand_prof
        self.env.num_rows = self.num_rows
        self.env.num_cols = self.num_cols
        self.latest_obs = self.env.reset()
        # Report success
        print('Created new environment {0} with GameID: {1}'.format(self.ENV_NAME, self.GAME_ID))

    def done(self):
        print("Episode finished after {} turns.".format(self.turn))
        pg.quit()
        self._cleanup()

    def _cleanup(self):
        self.env.close()

    def _draw_screen(self):
        # Update the screen with the new observation, use the grid object directly
        # Populate each cell
        for r_ in range(self.env.grid.rows):
            for c_ in range(self.env.grid.cols):
                cell = self.env.grid.grid[r_][c_]
                if cell.terrain == Terrains.none:
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.out_of_bounds:
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.wall:
                    cell_color = pg.color.Color(MapColors.wall_tile.value)
                elif cell.terrain == Terrains.floor:
                    cell_color = pg.color.Color(MapColors.floor_tile.value)
                # elif cell.terrain == Terrains.mud:
                #    cell_color = pg.color.Color(MapColors.mud_tile.value)
                elif cell.terrain == Terrains.fire:
                    cell_color = pg.color.Color(MapColors.fire_tile.value)
                elif cell.terrain == Terrains.hospital:
                    cell_color = pg.color.Color(MapColors.hospital_tile.value)
                else:
                    raise ValueError('Invalid cell terrain while rendering game image.')

                # Draw the rectangle with the right color for the terrains
                # rect is play area, color, and (left point, top point, width, height)
                pg.draw.rect(self.play_area, cell_color, (c_ * self.cell_size, r_ * self.cell_size,
                                                          self.cell_size, self.cell_size))
                self.game_screen.blit(self.play_area, self.play_area.get_rect())

                # Add in the cell value string
                pg.font.init()
                cell_font = pg.font.SysFont(pg.font.get_default_font(), 20)
                cell_val = self.env.grid.get_human_cell_value(r_, c_)
                # cell_val = '{},{}'.format(r_, c_)
                text_surf = cell_font.render(cell_val, True, pg.color.Color(MapColors.text.value))
                self.play_area.blit(text_surf, ((c_ * self.cell_size) + self.cell_size // 2,
                                                (r_ * self.cell_size) + self.cell_size // 2))
        pg.display.update()

    async def run(self):

        print('Starting new game with machine play!')
        print(f'Mode: {"Manual" if self.manual else "Automatic"}')
        # Set up pygame loop for game, capture actions, and redraw the screen on action
        self.latest_obs = self.env.reset()
        pg.init()
        self.game_screen = pg.display.set_mode((1000, 800))
        pg.display.set_caption('SGW Machine Play')
        self.play_area = pg.Surface((self.env.grid.rows * self.cell_size, self.env.grid.cols * self.cell_size))
        self.play_area.fill(pg.color.Color(MapColors.play_area.value))
        self.game_screen.fill(pg.color.Color(MapColors.game_screen.value))
        self._draw_screen()

        # Main game loop, capture window events, actions, and redraw the screen with updates until game over
        MOVE_EVENT = pg.USEREVENT + 1
        move = pg.event.Event(MOVE_EVENT)
        if not self.manual:
            pg.event.post(move)
        game_exit = False
        while not game_exit:
            for event in pg.event.get():

                # Exit game upon window close
                if event.type == pg.QUIT:
                    game_exit = True
                    self.done()

                if self.turn < self.max_turn and not self.is_game_over:

                    # Execute main turn logic
                    # Catch a common key stroke to advance to next machine turn
                    keep_playing = False
                    action = None
                    if self.manual:
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_ESCAPE:
                                game_exit = True
                                self.done()
                            if event.key in [pg.K_SPACE, pg.K_KP_ENTER, pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT,
                                             pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_0, pg.K_1, pg.K_2, pg.K_3]:
                                keep_playing = True
                    else:
                        if event.type == MOVE_EVENT:
                            keep_playing = True

                    if keep_playing:
                        # TODO: add logic to choose an action
                        action = choose_action(self.latest_obs)

                    if action is not None:
                        if action == Actions.quit:
                            game_exit = True
                            self.done()
                        if action in [Actions.step_forward, Actions.turn_right, Actions.turn_left, Actions.none]:
                            # We have a valid action, so let's process it and update the screen
                            encoded_action = self.env.encode_raw_action(action)  # Ensures clean action
                            action_decoded = self.env.decode_raw_action(encoded_action)

                            # Take a step, print the status, render the new state
                            observation, reward, done, info = self.env.step(encoded_action)
                            self.latest_obs = observation
                            self.env.pp_info()
                            self.is_game_over = done

                            observation = list(observation)
                            grid = dict()
                            for r_ in range(self.num_rows):
                                for c_ in range(self.num_cols):
                                    grid[f'{r_}, {c_}'] = observation[0][r_][c_].get_data()
                            observation[0] = json.dumps(grid)
                            observation = tuple(observation)

                            # Write action and stuff out to disk.
                            data_to_log = {
                                'game_id': str(self.GAME_ID),
                                'turn': self.turn,
                                'raw_action': action,
                                'action': action_decoded,
                                'reward': reward,
                                'game_done': done,
                                'game_info': {k.replace('.', '_'): v for (k, v) in info.items()},
                                'raw_state': str(observation)
                            }
                            with open(self.DATA_LOG_FILE_NAME, 'a') as f_:
                                f_.write(json.dumps(data_to_log) + '\n')
                                f_.close()

                            # Tick up turn
                            self.turn += 1
                            if self.is_game_over:
                                game_exit = True
                                self.done()

                            # Draw the screen
                            if not self.is_game_over:
                                self._draw_screen()
                                if not self.manual:
                                    pg.event.post(move)

                else:
                    # Else end the game
                    game_exit = True
                    self.done()

        pg.quit()
