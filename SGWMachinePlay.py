import json
import uuid
import gym
import gym_sgw  # Required, don't remove!
import pygame as pg
from gym_sgw.envs.enums.Enums import Actions, Terrains, PlayTypes, MapProfiles, MapColors
from choose_action import choose_action
import random

class SGW:
    """
    Machine play game variant using a pathfinding algorithm.
    """
    def __init__(self, data_log_file='data_log_machine.json', raw_states_file='raw_states_machine.json', final_data_file='final_data_machine.json', max_energy=50, map_file=None,
                 rand_prof=MapProfiles.concentrated, num_rows=25, num_cols=25, manual=False):
        self.ENV_NAME = 'SGW-v0'
        self.DATA_LOG_FILE_NAME = data_log_file
        self.RAW_STATES_FILE_NAME = raw_states_file
        self.FINAL_DATA_FILE_NAME = final_data_file
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
        self.terrain_blits = []
        self.text_blits = []
        self.last_data_logged = {}

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
                    cell_img = pg.image.load(MapColors.black_tile.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)
                elif cell.terrain == Terrains.wall:
                    cell_img = pg.image.load(MapColors.wall_tile.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)
                elif cell.terrain == Terrains.floor:
                    cell_img = pg.image.load(MapColors.floor_tile.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)
                elif cell.terrain == Terrains.future_fire:
                    floor_img = pg.image.load(MapColors.floor_tile.value)
                    floor_img = pg.transform.scale(floor_img, (self.cell_size, self.cell_size))
                    blit = (floor_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)

                    cell_img = pg.image.load(MapColors.future_fire_tile.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)
                elif cell.terrain == Terrains.fire:
                    # cell_color = pg.color.Color(MapColors.floor_tile.value)
                    floor_img = pg.image.load(MapColors.floor_tile.value)
                    floor_img = pg.transform.scale(floor_img, (self.cell_size, self.cell_size))
                    blit = (floor_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)

                    cell_img = pg.image.load(MapColors.fire_tile.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)
                elif cell.terrain == Terrains.hospital:
                    # cell_color = pg.color.Color(MapColors.floor_tile.value)
                    floor_img = pg.image.load(MapColors.floor_tile.value)
                    floor_img = pg.transform.scale(floor_img, (self.cell_size, self.cell_size))
                    blit = (floor_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit) 

                    cell_img = pg.image.load(MapColors.hospital_tile.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)
                else:
                    raise ValueError('Invalid cell terrain while rendering game image.')

                # Draw the rectangle with the right color for the terrains
                # rect is play area, color, and (left point, top point, width, height)
                # pg.draw.rect(self.play_area, cell_color, (c_ * self.cell_size, r_ * self.cell_size,
                #                                         self.cell_size, self.cell_size))
                # self.game_screen.blit(self.play_area, self.play_area.get_rect())

                # Add in the cell value string
                pg.font.init()
                cell_font = pg.font.SysFont(pg.font.get_default_font(), 20)
                cell_val = self.env.grid.get_human_cell_value(r_, c_)
                # cell_val = '{},{}'.format(r_, c_)
                if 'B' in cell_val:
                    cell_img = pg.image.load(MapColors.battery.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)

                elif '^' in cell_val:
                    cell_img = pg.image.load(MapColors.ambulance_up.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)
                elif 'v' in cell_val:
                    cell_img = pg.image.load(MapColors.ambulance_down.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)
                elif '<' in cell_val:
                    cell_img = pg.image.load(MapColors.ambulance_left.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)
                elif '>' in cell_val:
                    cell_img = pg.image.load(MapColors.ambulance_right.value)
                    cell_img = pg.transform.scale(cell_img, (self.cell_size, self.cell_size))
                    blit = (cell_img, (c_ * self.cell_size, r_ * self.cell_size))
                    self.terrain_blits.append(blit)

                if 'I' in cell_val:
                    text_surf = cell_font.render('I', True, pg.color.Color(MapColors.text.value))
                    # self.play_area.blit(text_surf, ((c_ * self.cell_size) + self.cell_size // 2,
                    #                                 (r_ * self.cell_size) + self.cell_size // 2))
                    text_blit = (text_surf, ((c_ * self.cell_size) + self.cell_size // 2,
                                            (r_ * self.cell_size) + self.cell_size // 2))
                    self.text_blits.append(text_blit)

        # energy bar & text
        energy_bg, energy_color = pg.color.Color('#86868cff'), pg.color.Color("#3ddb62")
        pg.draw.rect(self.game_screen, energy_bg, (650, 100, 300, 50))
        if self.env.get_energy_remaining() < 94: 
            energy_width = self.env.get_energy_remaining() * 3
        else: 
            energy_width = 280
        pg.draw.rect(self.game_screen, energy_color, (660, 110, energy_width, 30))
        pg.draw.rect(self.game_screen, pg.color.Color(MapColors.game_screen.value), (650, 50, 300, 50))
        energy_font = pg.font.SysFont(pg.font.get_default_font(), 32)
        text = energy_font.render('Energy Remaining: ' + str(self.env.get_energy_remaining()), 
                                  True, pg.color.Color(MapColors.text.value))
        self.text_blits.append((text, (650, 70)))
        pg.display.update()

    def _draw_icons(self):
        self.game_screen.blits(self.terrain_blits)
        self.game_screen.blits(self.text_blits)
        pg.display.update()
        self.terrain_blits, self.text_blits = [], []

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
                self._draw_icons()
                # Exit game upon window close
                if event.type == pg.QUIT:
                    game_exit = True
                    with open(self.FINAL_DATA_FILE_NAME, 'a') as f_:
                        f_.write(json.dumps(self.last_data_logged) + '\n')
                        f_.close()
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
                                with open(self.FINAL_DATA_FILE_NAME, 'a') as f_:
                                    f_.write(json.dumps(self.last_data_logged) + '\n')
                                    f_.close()
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
                            with open(self.FINAL_DATA_FILE_NAME, 'a') as f_:
                                f_.write(json.dumps(self.last_data_logged) + '\n')
                                f_.close()
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
                                'percent_saved': self.env.grid.get_percent_saved(),
                                'object_data': self.env.grid.object_data
                            }

                            self.last_data_logged = data_to_log

                            raw_state = {'game_id': str(self.GAME_ID), 
                                         'turn': self.turn,
                                         'raw_state': observation}
                            with open(self.DATA_LOG_FILE_NAME, 'a') as f_:
                                f_.write(json.dumps(data_to_log) + '\n')
                                f_.close()

                            with open(self.RAW_STATES_FILE_NAME, 'a') as file_:
                                file_.write(json.dumps(raw_state) + '\n')
                                file_.close()

                            # Tick up turn
                            self.turn += 1
                            if self.is_game_over or self.env.grid.ped_on_map() == False:
                                game_exit = True
                                with open(self.FINAL_DATA_FILE_NAME, 'a') as f_:
                                    f_.write(json.dumps(data_to_log) + '\n')
                                    f_.close()
                                self.done()

                            # Draw the screen
                            if not self.is_game_over:
                                self._draw_screen()
                                if not self.manual:
                                    pg.event.post(move)

                else:
                    # Else end the game
                    game_exit = True
                    with open(self.FINAL_DATA_FILE_NAME, 'a') as f_:
                        f_.write(json.dumps(self.last_data_logged) + '\n')
                        f_.close()
                    self.done()

        pg.quit()
