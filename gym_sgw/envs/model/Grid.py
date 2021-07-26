import random
import json
import xlrd
from typing import List
import numpy as np
import pygame as pg
from gym_sgw.envs.model.Cell import Cell
from gym_sgw.envs.enums.Enums import MapObjects, Terrains, Actions, Orientations, MapProfiles, MapColors, Concentrations
from gym_sgw.envs.model.Pedestrian import Pedestrian


class Grid:

    def __init__(self, map_file: str = None, rows=25, cols=25, random_profile: MapProfiles = MapProfiles.simple):
        self.ped_list = Pedestrian()
        self.concentration = random.randint(0, 3)
        self.map_file = map_file
        self.rows = rows
        self.cols = cols
        self.random_profile = random_profile
        self.player_orientation = None
        self.player_location = None
        self.grid = self.read_in_map() if map_file is not None else self.random_grid()
        self.map_max_energy = None
        self.initial_peds = self.ped_list.get_num_peds()

    def read_in_map(self):

        # Hard-coded Constants
        SYMBOL_PLAYER_LIST = ['^', '>', 'v', '<']
        SYMBOL_INJURED = '*'
        # SYMBOL_ZOMBIE = 'Z'
        SYMBOL_BATTERY = '#'
        SHEET_INDEX = 0

        # Open Excel file
        book = xlrd.open_workbook(self.map_file, formatting_info=True)

        # Each sheet (tabs at the bottom) contains 1 map
        sheet = book.sheet_by_index(SHEET_INDEX)
        print('Loading Map: {}'.format(sheet.name))

        # Get constants defined in spreadsheet -- cells are 0 indexed (hardcoded references for now)
        max_width = int(sheet.cell(19, 3).value)
        max_height = int(sheet.cell(20, 3).value)
        start_row = int(sheet.cell(21, 3).value) - 1
        start_col = int(sheet.cell(22, 3).value) - 1
        self.map_max_energy = int(sheet.cell(25, 3).value)

        color_indexes = {}
        # Get color constants for terrain, found in the legend
        for i in range(7):
            xfx = sheet.cell_xf_index(2 + i, 1)
            xf = book.xf_list[xfx]
            bgx = xf.background.pattern_colour_index
            color_indexes[bgx] = i  # i = enum value, where 0 = none, etc.

        # Get end rows and cols of map
        max_rows = min(sheet.nrows, start_row + max_height)
        max_cols = min(sheet.ncols, start_col + max_width)
        end_row = start_row
        end_col = start_col

        # Get the bounds of the map
        for row_ in range(start_row, max_rows):
            for col_ in range(start_col, max_cols):
                cell = sheet.cell(row_, col_)
                xfx = sheet.cell_xf_index(row_, col_)
                xf = book.xf_list[xfx]
                bgx = xf.background.pattern_colour_index
                # Check if cell is empty
                if not cell.value and color_indexes[bgx] == 0:
                    continue
                # otherwise update the end_row and end_col
                else:
                    end_row = max(end_row, row_)
                    end_col = max(end_col, col_)

        # Set the bounds of the map
        num_rows = end_row - start_row + 1
        num_cols = end_col - start_col + 1

        # Update important things based on the read in map
        self.rows = num_rows
        self.cols = num_cols

        grid = []
        for r_ in range(num_rows):
            grid_row = []
            for c_ in range(num_cols):
                row_, col_ = r_ + start_row, c_ + start_col
                sheet_cell = sheet.cell(row_, col_)
                xfx = sheet.cell_xf_index(row_, col_)
                xf = book.xf_list[xfx]
                bgx = xf.background.pattern_colour_index
                # Terrain
                if bgx in color_indexes:
                    grid_cell = Cell(Terrains(color_indexes[bgx]))
                else:
                    grid_cell = Cell()
                # Objects
                if sheet_cell.value in SYMBOL_PLAYER_LIST:
                    grid_cell.add_map_object(MapObjects.player)
                    self.player_location = [r_, c_]
                    if sheet_cell.value == '^':
                        self.player_orientation = Orientations.up
                    elif sheet_cell.value == '>':
                        self.player_orientation = Orientations.right
                    elif sheet_cell.value == 'v':
                        self.player_orientation = Orientations.down
                    elif sheet_cell.value == '<':
                        self.player_orientation = Orientations.left
                    else:
                        raise ValueError('Invalid player icon')
                elif sheet_cell.value == SYMBOL_INJURED:
                    grid_cell.add_map_object(MapObjects(1))
                # elif sheet_cell.value == SYMBOL_ZOMBIE:
                #    grid_cell.add_map_object(MapObjects(3))
                elif sheet_cell.value == SYMBOL_BATTERY:
                    grid_cell.add_map_object(MapObjects(4))

                # Add cell to grid[][]
                grid_row.append(grid_cell)

            grid.append(grid_row)

        return grid

    def random_grid(self):
        empty_grid = self._get_empty_grid_with_boarders()
        random_grid = self._random_fill_setup(empty_grid)
        return random_grid

    def _get_empty_grid_with_boarders(self) -> List:
        grid = list()
        for r_ in range(self.rows):
            row_data = []
            for c_ in range(self.cols):
                # Put edges to the top and bottom
                if r_ == 0 or r_ == self.rows - 1:
                    cell_data = Cell(Terrains.out_of_bounds)
                # Put edges to the left and right
                elif c_ == 0 or c_ == self.cols - 1:
                    cell_data = Cell(Terrains.out_of_bounds)
                # Set normal defaults then
                else:
                    cell_data = Cell(Terrains.floor)
                row_data.append(cell_data)
            grid.append(row_data)
        return grid

    def _random_fill_setup(self, grid):
        # This replicates the excel workbook that generates random maps. Directly implemented for ease of use.
        # The only difference is that this implementation also adds the player with a valid orientation.

        # Define map element's cumulative probability table based on the mode (magic numbers tuned by instructors)
        mode = self.random_profile

        if mode == MapProfiles.trolley:
            p_wall = 30
            p_floor = 79
            p_hospital = 80
            p_fire = 83
            # p_mud = 86
            p_injured = 89
            # p_zombie = 99
            p_battery = 100
        elif mode == MapProfiles.sparse:
            p_wall = 20
            p_floor = 79
            p_hospital = 80
            p_fire = 83
            # p_mud = 86
            p_injured = 89
            # p_zombie = 99
            p_battery = 100
        elif mode == MapProfiles.pacman:
            p_wall = 35
            p_floor = 65
            p_hospital = 65
            p_fire = 65
            # p_mud = 65
            p_injured = 65
            # p_zombie = 95
            p_battery = 100
        elif mode == MapProfiles.spoiled:
            p_wall = 10
            p_floor = 64
            p_hospital = 69
            p_fire = 72
            # p_mud = 75
            p_injured = 95
            # p_zombie = 100
            p_battery = 100
        elif mode == MapProfiles.twisty:
            p_wall = 37
            p_floor = 88
            p_hospital = 89
            p_fire = 90
            # p_mud = 91
            p_injured = 96
            # p_zombie = 96
            p_battery = 100
        elif mode == MapProfiles.volcano:
            p_wall = 2
            p_floor = 53
            p_hospital = 54
            p_fire = 79
            # p_mud = 91
            p_injured = 96
            # p_zombie = 96
            p_battery = 100
        elif mode == MapProfiles.simple:
            p_wall = 5
            p_floor = 50
            p_hospital = 60
            p_fire = 70
            p_injured = 90
            p_battery = 100
        elif mode == MapProfiles.concentrated:
            p_wall = 5
            p_floor = 50
            p_hospital = 60
            p_fire = 80
            p_injured = 90
            p_battery = 100
        else:  # Default to the uniform case
            p_wall = 11
            p_floor = 23
            p_hospital = 34
            p_fire = 45
            # p_mud = 56
            p_injured = 67
            # p_zombie = 89
            p_battery = 100

        # for each cell in the grid
        for r_ in range(len(grid)):
            for c_ in range(len(grid[r_])):
                # Start the player in the middle of the grid facing right
                if r_ == int(self.rows // 2) and c_ == int(self.cols // 2):
                    grid[r_][c_].add_map_object(MapObjects.player)
                    self.player_location = [r_, c_]
                    self.player_orientation = Orientations.right
                    continue
                curr_cell = grid[r_][c_]

                # Leave in place any boarder walls that we may have set already in the grid when we initialized it.
                if curr_cell.terrain is Terrains.out_of_bounds:
                    continue

                if mode == MapProfiles.concentrated:
                    r_border, c_border = self._get_fire_borders(grid)

                # Get a random int between 1 and 100, note these bounds are both inclusive
                cell_roll = random.randint(1, 100)  # We could use a random continuous value if we wanted too!
                if cell_roll < p_wall:
                    grid[r_][c_].terrain = Terrains.wall
                elif cell_roll < p_floor:
                    grid[r_][c_].terrain = Terrains.floor
                elif cell_roll < p_hospital:
                    grid[r_][c_].terrain = Terrains.hospital
                elif cell_roll < p_fire:
                    if mode == MapProfiles.concentrated:
                        self._fill_concentrations(grid, r_border, c_border, r_, c_)
                    else:
                        grid[r_][c_].terrain = Terrains.fire
                # elif cell_roll < p_mud:
                #    grid[r_][c_].terrain = Terrains.mud
                elif cell_roll < p_injured:
                    grid[r_][c_].add_map_object(MapObjects.injured)
                    self.ped_list.add_ped(r_, c_)
                # elif cell_roll < p_zombie:
                #    grid[r_][c_].add_map_object(MapObjects.zombie)
                elif cell_roll <= p_battery:
                    grid[r_][c_].add_map_object(MapObjects.battery)
                else:
                    raise RuntimeError('Random cell value out of range?')
        return grid

    def _get_fire_borders(self, grid):
        # returns the row and column borders for concentrated fire
        if self.concentration == Concentrations.upper_left:
            r_border, c_border = self.rows//5 + 1, self.cols//5 + 1
        elif self.concentration == Concentrations.bottom_left:
            r_border, c_border = self.rows - (self.rows//5) - 1, self.cols//5 + 1
        elif self.concentration == Concentrations.upper_right:
            r_border, c_border = self.rows//5 + 1, self.cols - (self.cols//5) - 1
        elif self.concentration == Concentrations.bottom_right:
            r_border, c_border = self.rows - (self.rows//5) - 1, self.cols - (self.cols//5) - 1
        return r_border, c_border

    def _fill_concentrations(self, grid, r_border, c_border, r_, c_, fire=True):
        # fills fire and hospital squares for concentrations
        if self.concentration == Concentrations.upper_left and r_ < r_border and c_ < c_border:
            grid[r_][c_].terrain = Terrains.fire
        elif self.concentration == Concentrations.bottom_left and r_ > r_border and c_ < c_border:
            grid[r_][c_].terrain = Terrains.fire
        elif self.concentration == Concentrations.upper_right and r_ < r_border and c_ > c_border:
            grid[r_][c_].terrain = Terrains.fire
        elif self.concentration == Concentrations.bottom_right and r_ > r_border and c_ > c_border:
            grid[r_][c_].terrain = Terrains.fire

    def do_turn(self, action: Actions):

        # Update player position based on current location and orientation
        if action == Actions.step_forward:
            self._execute_step_forward()
        # Update player orientation
        elif action == Actions.turn_left:
            self._execute_turn_left()
        elif action == Actions.turn_right:
            self._execute_turn_right()
        # Didn't find a valid action so defaulting to none
        elif action == Actions.none:
            pass
        else:
            raise ValueError('Invalid action found while attempting to do turn on the Grid.')

        # Process penalties and rewards
        # Baseline score, energy numbers for each move, modify these based on the cell we end up at
        turn_score = self._get_score_of_action()  # Total score is captured in the env
        energy_action = self._get_energy_of_action()  # can be negative if gained energy
        done = False  # always false, the game object will keep track of total energy and total score

        return turn_score, energy_action, done

    # take away hp from every pedestrian on fire terrain
    def burn_pedestrian(self):
        turn_score = 0

        # find cells with fire
        for r_ in range(1, self.rows):
            for c_ in range(1, self.cols):
                cell = self.grid[r_][c_]
                if cell.terrain == Terrains.fire:
                    # check if cells with fire also contain pedestrian object
                    if self.ped_list.exists(location=(r_, c_)):
                        self.ped_list.hurt(r_, c_)
                        # check if pedestrian objects have run out of hp
                        if self.ped_list.get_hp((r_, c_)) <= 0:
                            self.ped_list.remove_ped(r_, c_)
                            cell.remove_map_object(MapObjects.injured)
                            turn_score += self._get_score_of_other()  # negative reward for pedestrian burn death

        return turn_score

    def move_fire(self):
        # Locate predicted squares & change to fire
        for r_ in range(1, self.rows):
            for c_ in range(1, self.cols):
                cell = self.grid[r_][c_]
                if cell.terrain == Terrains.future_fire:
                    cell.terrain = Terrains.fire

    def predict_fire(self):
        # locate current cells w/ fire
        for r_ in range(1, self.rows):
            for c_ in range(1, self.cols):
                cell = self.grid[r_][c_]
                if cell.terrain == Terrains.fire:
                    # locate and save available adjacent cells
                    free_cells= []
                    for adjacent_cell in [self.grid[r_+1][c_], self.grid[r_][c_+1], 
                                          self.grid[r_-1][c_], self.grid[r_][c_-1], 
                                          self.grid[r_-1][c_], self.grid[r_-1][c_]]:
                        if adjacent_cell.terrain == Terrains.floor:
                            free_cells.append(adjacent_cell)
                    # may need to use other random function for skewed spread
                    if free_cells != []:
                        next_cell = random.choice(free_cells)
                        next_cell.terrain = Terrains.future_fire

    def get_percent_saved(self):
        percent = 1 - self.ped_list.get_num_peds()/self.initial_peds
        return (round(percent, 2))*100

    def _execute_step_forward(self):

        # Get the next position based on orientation
        curr_pos = self.player_location
        if self.player_orientation == Orientations.right:
            next_pos = [curr_pos[0], curr_pos[1] + 1]
        elif self.player_orientation == Orientations.left:
            next_pos = [curr_pos[0], curr_pos[1] - 1]
        elif self.player_orientation == Orientations.up:
            next_pos = [curr_pos[0] - 1, curr_pos[1]]
        elif self.player_orientation == Orientations.down:
            next_pos = [curr_pos[0] + 1, curr_pos[1]]
        else:
            raise RuntimeError('Invalid orientation when trying to move forward')

        # Check validity of move
        if not self._is_valid_move(next_pos):
            next_pos = curr_pos

        # Update the player's position
        self.player_location = next_pos

        # Grab the current and next cell
        curr_cell = self.grid[curr_pos[0]][curr_pos[1]]
        next_cell = self.grid[next_pos[0]][next_pos[1]]

        # Update the player's position in the cells
        curr_cell.remove_map_object(MapObjects.player)
        next_cell.add_map_object(MapObjects.player)

        # Update the map objects in cells so they move with the player (update injured, passengers)
        if MapObjects.injured in curr_cell.objects:
            curr_cell.remove_map_object(MapObjects.injured)
            next_cell.add_map_object(MapObjects.injured)
            self.ped_list.remove_ped(curr_pos[0], curr_pos[1])

    def _execute_turn_left(self):
        if self.player_orientation == Orientations.right:
            self.player_orientation = Orientations.up
        elif self.player_orientation == Orientations.left:
            self.player_orientation = Orientations.down
        elif self.player_orientation == Orientations.up:
            self.player_orientation = Orientations.left
        elif self.player_orientation == Orientations.down:
            self.player_orientation = Orientations.right
        else:
            raise RuntimeError('Invalid orientation when trying to change orientation left')

    def _execute_turn_right(self):
        if self.player_orientation == Orientations.right:
            self.player_orientation = Orientations.down
        elif self.player_orientation == Orientations.left:
            self.player_orientation = Orientations.up
        elif self.player_orientation == Orientations.up:
            self.player_orientation = Orientations.right
        elif self.player_orientation == Orientations.down:
            self.player_orientation = Orientations.left
        else:
            raise RuntimeError('Invalid orientation when trying to change orientation right')

    def _get_score_of_action(self):
        # Default Reward Scheme
        RESCUE_REWARD = 9  # +9 per rescued victim (picked up one by one and delivered to hospital)
        VIC_PENALTY = -1  # -1 per squished victim (if you already have one onboard and enter it’s space, SQUISH)
        # FIRE_PENALTY = -5  # -5 per entry into fire (each entry; but otherwise it doesn’t actually hurt you)
        # ZOMBIE_REWARD = 2  # +2 per squished zombie (ZOMBIE DEATH!)
        t_score = 0

        # Grab the cell where the player is (after the move)
        end_cell: Cell = self.grid[self.player_location[0]][self.player_location[1]]

        # Add a reward if they rescued a victim
        if end_cell.terrain == Terrains.hospital:
            if MapObjects.injured in end_cell.objects:
                t_score += RESCUE_REWARD  # Deliver the injured
                end_cell.remove_map_object(MapObjects.injured)  # Remove them from the board

        # Add a penalty if you squish an injured person
        if end_cell.objects.count(MapObjects.injured) > 1:
            t_score += VIC_PENALTY  # Can only carry one so if there's more than one, squish
            end_cell.remove_map_object(MapObjects.injured)

        # Add a penalty for going into fire
        # if end_cell.terrain == Terrains.fire:
        #     t_score += FIRE_PENALTY  # ouch

        # Add reward for squishing a zombie
        # if MapObjects.zombie in end_cell.objects:
        #    t_score += ZOMBIE_REWARD  # RUN IT OVER!
        #    end_cell.remove_map_object(MapObjects.zombie)

        return t_score

    # calculate reward of things that aren't technically player actions
    # basically only for pedestrians dying in fire rn
    def _get_score_of_other(self):
        BURN_PENALTY = -1  # placeholder value; can change
        t_score = 0

        t_score += BURN_PENALTY  # :(

        return t_score

    def _get_energy_of_action(self):
        # Default energy scheme
        BAT_POWER = 20  # Battery = + 20 energy
        #MUD_DRAIN = -5  # Mud = 5 energy penalty
        BASE_ENERGY = -1  # All moves costs something
        FIRE_DRAIN = -3  # placeholder value; can change
        t_energy = 0

        # Grab the cell where the player is (after the move)
        end_cell: Cell = self.grid[self.player_location[0]][self.player_location[1]]

        # Add energy if you hit a battery (and remove it from the board)
        if MapObjects.battery in end_cell.objects:
            t_energy += BAT_POWER  # I HAAAAVVVEEEEEE THEEEE POOWEEERRRRRRRRRRR
            end_cell.remove_map_object(MapObjects.battery)

        # Drain energy if you hit mud (do not remove it from the board)
        # if end_cell.terrain == Terrains.mud:
        #    t_energy += MUD_DRAIN  # wah wah

        # drain energy if you hit fire
        if end_cell.terrain == Terrains.fire:
            t_energy += FIRE_DRAIN

        # Add in base energy
        t_energy += BASE_ENERGY

        return t_energy

    def _is_valid_move(self, pos) -> bool:
        # Don't let the player move out of bounds or through walls
        curr_cell = self.grid[pos[0]][pos[1]]
        return curr_cell.terrain not in [Terrains.none, Terrains.out_of_bounds, Terrains.wall]

    def get_human_cell_value(self, row, col):

        cell = self.grid[row][col]
        cell_val = ''
        if MapObjects.none in cell.objects:
            cell_val += '?'
        if MapObjects.player in cell.objects:
            if self.player_orientation == Orientations.up:
                p_icon = '^'
            elif self.player_orientation == Orientations.down:
                p_icon = 'v'
            elif self.player_orientation == Orientations.left:
                p_icon = '<'
            elif self.player_orientation == Orientations.right:
                p_icon = '>'
            else:
                raise ValueError('Invalid player orientation while retrieving cell value for encoding/decoding')
            cell_val += p_icon
        if MapObjects.battery in cell.objects:
            cell_val += 'B'
        if MapObjects.injured in cell.objects:
            cell_val += 'I'
        #if MapObjects.zombie in cell.objects:
        #    cell_val += 'Z'

        return cell_val

    def _get_machine_cell_value(self, row, col):

        # Encode each cell value with an integer between 0 and 70
        # The ten's place is a map of the terrains as follows:
        #     none = 00's
        #     out_of_bounds = 10's
        #     wall = 20's
        #     floor = 30's
        #     mud = 40's
        #     fire = 50's
        #     hospital = 60's
        # The one's place is a map of the map object as follows:
        #     none = 0
        #     injured = 1
        #     zombie = 3
        #     battery = 4
        #     player_up = 5
        #     player_down = 6
        #     player_left = 7
        #     player_right = 8

        cell = self.grid[row][col]
        cell_val = 0

        # Get the ten's place based on the terrain, only ever one kind of terrain
        if cell.terrain == Terrains.none:
            cell_val += 0
        elif cell.terrain == Terrains.out_of_bounds:
            cell_val += 10
        elif cell.terrain == Terrains.wall:
            cell_val += 20
        elif cell.terrain == Terrains.floor:
            cell_val += 30
        elif cell.terrain == Terrains.future_fire:
            cell_val += 40
        elif cell.terrain == Terrains.fire:
            cell_val += 50
        elif cell.terrain == Terrains.hospital:
            cell_val += 60
        else:
            raise ValueError('Invalid cell terrain while retrieving cell value for encoding/decoding.')

        # Technically supports more than one object so order here matters
        if MapObjects.player in cell.objects:
            if self.player_orientation == Orientations.up:
                cell_val += 5
            elif self.player_orientation == Orientations.down:
                cell_val += 6
            elif self.player_orientation == Orientations.left:
                cell_val += 7
            elif self.player_orientation == Orientations.right:
                cell_val += 8
            else:
                raise ValueError('Invalid player orientation while retrieving cell value for encoding/decoding')
        elif MapObjects.injured in cell.objects:
            cell_val += 1
        elif MapObjects.battery in cell.objects:
            cell_val += 4
        # elif MapObjects.zombie in cell.objects:
        #    cell_val += 3
        elif MapObjects.none in cell.objects:
            cell_val += 0
        else:
            # No objects assigned to cell
            cell_val += 0  # Mark it the same as none for the machine

        return cell_val

    def human_encode(self, turns_executed, action_taken, energy_remaining, game_score):
        # Package up "Grid" object in a way that is viewable to humans (multi-line string)
        grid_data = dict()
        for r_ in range(self.rows):
            for c_ in range(self.cols):
                grid_data[f'{r_}, {c_}'] = self.grid[r_][c_].get_data()
        grid_data['status'] = {
            'turns_executed': turns_executed,
            'action_taken': action_taken,
            'energy_remaining': energy_remaining,
            'game_score': game_score,
            'percent_saved': self.get_percent_saved()
        }
        return json.dumps(grid_data)

    def machine_encode(self, turns_executed, action_taken, energy_remaining, game_score):
        grid_data = {
            'turns_executed': turns_executed,
            'action_taken': action_taken,
            'energy_remaining': energy_remaining,
            'game_score': game_score,
            'player_location': self.player_location,
            'player_orientation': self.player_orientation,
            'percent_saved': self.get_percent_saved()
        }
        return self.grid, grid_data

    def render(self, turns_executed, action_taken, energy_remaining, game_score, cell_size=30):
        # Print out the human encoding to standard out
        print('Turns Executed: {0} | Action: {1} | Energy Remaining: {2} | '
              'Score: {3} | Full State: {4}'.format(turns_executed, action_taken,
                                                    energy_remaining, game_score,
                                                    self.human_encode(turns_executed, action_taken,
                                                                      energy_remaining, game_score)))

        # Show a nicer display
        pg.init()
        game_screen = pg.display.set_mode((1000, 800))
        pg.display.set_caption("SGW")
        play_area = pg.Surface((self.rows * cell_size, self.cols * cell_size))
        play_area.fill(pg.color.Color(MapColors.play_area.value))
        game_screen.fill(pg.color.Color(MapColors.game_screen.value))

        # Populate each cell
        for r_ in range(self.rows):
            for c_ in range(self.cols):

                # Set the right background color
                cell = self.grid[r_][c_]
                if cell.terrain == Terrains.none:
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.out_of_bounds:
                    cell_color = pg.color.Color(MapColors.black_tile.value)
                elif cell.terrain == Terrains.wall:
                    cell_color = pg.color.Color(MapColors.wall_tile.value)
                elif cell.terrain == Terrains.floor:
                    cell_color = pg.color.Color(MapColors.floor_tile.value)
                elif cell.terrain == Terrains.future_fire:
                    cell_color = pg.color.Color(MapColors.future_fire_tile.value)
                elif cell.terrain == Terrains.fire:
                    cell_color = pg.color.Color(MapColors.fire_tile.value)
                elif cell.terrain == Terrains.hospital:
                    cell_color = pg.color.Color(MapColors.hospital_tile.value)
                else:
                    raise ValueError('Invalid cell terrain while rendering game image.')

                # Draw the rectangle with the right color for the terrains
                # rect is play area, color, and (left point, top point, width, height)
                pg.draw.rect(play_area, cell_color, (c_ * cell_size, r_ * cell_size, cell_size, cell_size))
                game_screen.blit(play_area, play_area.get_rect())

                # Add in the cell value string
                pg.font.init()
                cell_font = pg.font.SysFont(pg.font.get_default_font(), 20)
                cell_val = self.get_human_cell_value(r_, c_)
                text_surf = cell_font.render(cell_val, True, pg.color.Color(MapColors.text.value))
                play_area.blit(text_surf, ((c_ * cell_size) + cell_size // 2, (r_ * cell_size) + cell_size // 2))

        # Handle window events and allow for the window to be closed
        game_exit = False
        while not game_exit:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game_exit = True
            pg.display.update()
        pg.quit()

    @staticmethod
    def pp_info(turns_executed, action_taken, energy_remaining, game_score, percent_saved):
        print('Turns Executed: {0} | Action: {1} | Energy Remaining: {2} | '
              'Score: {3} | Percent Saved: {4}'.format(turns_executed, action_taken, energy_remaining, 
                                                       game_score, percent_saved))


if __name__ == '__main__':
    my_grid = Grid()
    score, energy, is_done = my_grid.do_turn(Actions.step_forward)
    my_grid.human_render(0, 'test', 50, 0)
    new_location = my_grid.player_location
    new_cell = my_grid.grid[new_location[0]][new_location[1]]
    print(str(new_cell.get_data()) + '  @ loc: {}'.format(new_location))
