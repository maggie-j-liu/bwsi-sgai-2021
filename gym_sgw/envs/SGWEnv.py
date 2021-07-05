from typing import Union
import gym
from gym import spaces
from gym_sgw.envs.enums.Enums import Actions, PlayTypes, MapProfiles, Terrains, MapObjects
from gym_sgw.envs.model.Grid import Grid
from gym_sgw.envs.Print_Colors.PColor import PBack


class SGW(gym.Env):

    def __init__(self):
        # Tunable parameters
        self.play_type = PlayTypes.machine
        self.render_mode = PlayTypes.machine
        self.max_energy = 50
        self.map_file = None
        self.rand_profile = MapProfiles.uniform
        # Grid set up
        self.num_rows = 20
        self.num_cols = 20
        self.grid = Grid(map_file=self.map_file, cols=self.num_cols, rows=self.num_rows,
                         random_profile=self.rand_profile)
        # Main parameters
        self.total_score = 0
        self.energy_used = 0
        self.is_game_over = False
        self.latest_action = self.decode_raw_action(Actions.none)
        self.turns_executed = 0
        # Defining spaces
        self._num_actions = len(Actions)
        self.action_space = None  # Build on reset, which is called after the init, don't build the grid twice
        self.observation_space = None  # Build on reset, which is called after the init, don't build the grid twice
        self.reset()

    def reset(self):
        self.grid = Grid(map_file=self.map_file, cols=self.num_cols, rows=self.num_rows,
                         random_profile=self.rand_profile)
        self.total_score = 0
        self.energy_used = 0
        self.max_energy = self.grid.map_max_energy if self.grid.map_max_energy is not None else self.max_energy
        self.is_game_over = False
        self.latest_action = self.decode_raw_action(Actions.none)
        self.turns_executed = 0
        self._num_actions = len(Actions)
        self.action_space = spaces.Discrete(self._num_actions)
        self.observation_space = spaces.Box(low=0, high=70, shape=(self.num_rows + 1, self.num_cols), dtype='uint8')
        obs = self.get_obs()
        return obs

    def step(self, raw_action: Actions):

        # Ensure that our type assertion holds
        action = self.encode_raw_action(raw_action)

        # Adjudicate turn
        turn_score, turn_energy, is_done = self._do_turn(action=action)
        self.latest_action = self.decode_raw_action(action)
        self.turns_executed += 1

        # Update score and turn counters
        self.total_score += turn_score
        self.energy_used += turn_energy

        # Check if done
        if is_done or (abs(self.energy_used) >= self.max_energy):
            self.is_game_over = True

        # Report out basic information for step
        obs = self.get_obs()
        info = {'turn_reward': turn_score, 'total_reward': self.total_score,
                'turn_energy_used': turn_energy, 'total_energy_used': self.energy_used,
                'total_energy_remaining': self.max_energy + self.energy_used}

        return obs, self.total_score, self.is_game_over, info

    def _do_turn(self, action):
        score, energy, done = self.grid.do_turn(action=action)
        return score, energy, done

    def get_obs(self):
        if self.play_type == PlayTypes.human:
            return self.grid.human_encode(turns_executed=self.turns_executed,
                                          action_taken=self.latest_action,
                                          energy_remaining=(self.max_energy + self.energy_used),
                                          game_score=self.total_score)
        elif self.play_type == PlayTypes.machine:
            return self.grid.machine_encode(turns_executed=self.turns_executed,
                                            action_taken=self.latest_action,
                                            energy_remaining=(self.max_energy + self.energy_used),
                                            game_score=self.total_score)
        else:
            raise ValueError('Failed to find acceptable play type.')

    def render(self, mode: PlayTypes = PlayTypes.human):
        if self.render_mode == PlayTypes.human or mode == PlayTypes.human:
            return self.grid.human_render(turns_executed=self.turns_executed,
                                          action_taken=self.latest_action,
                                          energy_remaining=(self.max_energy + self.energy_used),
                                          game_score=self.total_score, cell_size=30)
        elif self.render_mode == PlayTypes.machine or mode == PlayTypes.machine:
            return self.grid.machine_render(turns_executed=self.turns_executed,
                                            action_taken=self.latest_action,
                                            energy_remaining=(self.max_energy + self.energy_used),
                                            game_score=self.total_score)
        else:
            raise ValueError('Failed to find acceptable play type.')

    def pp_info(self):
        self.grid.pp_info(turns_executed=self.turns_executed,
                          action_taken=self.latest_action,
                          energy_remaining=(self.max_energy + self.energy_used),
                          game_score=self.total_score)

    @staticmethod
    def encode_raw_action(input_str: Union[str, Actions]) -> Actions:
        # Takes in some input string and tries to parse it to a valid action, encoding it in our enum
        # Use this if you want to go from a string or key press to an Actions Enum!
        if input_str in ['none', '', 'r_key', 0, '0', Actions.none]:
            return Actions.none
        if input_str in ['turn_left', 'left', 'left_arrow_key', 'a_key', 1, '1', Actions.turn_left]:
            return Actions.turn_left
        if input_str in ['turn_right', 'right', 'right_arrow_key', 'd_key', 2, '2', Actions.turn_right]:
            return Actions.turn_right
        if input_str in ['step_forward', 'forward', 'step', 'move', 'space_key', 3, '3', Actions.step_forward]:
            return Actions.step_forward
        print('WARNING: no valid action found while encoding action: {}'.format(input_str))
        return Actions.none

    @staticmethod
    def decode_raw_action(action: Actions) -> (str, int):
        # Reverse process of the encoding, takes in an enum action and spits out an unboxable decoding of the action
        # Use this to make the Actions Enum more readable, returns the label and int value for the enum.
        # Use if you want to go from Enum to something more understandable.
        return action.name, action.value

    @staticmethod
    def print_player_action_selections():

        # Build up console output
        buffer = '*' * 35
        player_action_string = PBack.blue + buffer + PBack.reset + '\n'

        player_action_string += PBack.blue + '**||' + PBack.reset + \
                                PBack.purple + ' Action ID'.center(10) + PBack.reset + \
                                PBack.blue + '||' + PBack.reset + \
                                PBack.purple + ' Action'.center(15) + PBack.reset + \
                                PBack.blue + '||**' + PBack.reset + '\n'

        for i in range(len(Actions)):
            act_val = str(Actions(i).value)
            act_name = Actions(i).name
            player_action_string += PBack.blue + '**||' + PBack.reset + \
                                    act_val.center(10) + \
                                    PBack.blue + '||' + PBack.reset + \
                                    act_name.center(15) + \
                                    PBack.blue + '||**' + PBack.reset + '\n'

        player_action_string += PBack.blue + buffer + PBack.reset

        print(player_action_string)
        return player_action_string

    @staticmethod
    def print_state_key():

        # Build up console output
        buffer = '*' * 35
        state_key_string = PBack.blue + buffer + PBack.reset + '\n'

        state_key_string += PBack.blue + '**||' + PBack.reset + \
                            PBack.purple + 'State Mark'.center(10) + PBack.reset + \
                            PBack.blue + '||' + PBack.reset + \
                            PBack.purple + 'Meaning'.center(15) + PBack.reset + \
                            PBack.blue + '||**' + PBack.reset + '\n'

        for terrain_index in range(len(Terrains)):
            # Get the right color from the map
            if Terrains(terrain_index) == Terrains.none:
                cell_color = PBack.black
            elif Terrains(terrain_index) == Terrains.out_of_bounds:
                cell_color = PBack.black
            elif Terrains(terrain_index) == Terrains.wall:
                cell_color = PBack.darkgrey
            elif Terrains(terrain_index) == Terrains.floor:
                cell_color = PBack.lightgrey
            elif Terrains(terrain_index) == Terrains.mud:
                cell_color = PBack.orange
            elif Terrains(terrain_index) == Terrains.fire:
                cell_color = PBack.red
            elif Terrains(terrain_index) == Terrains.hospital:
                cell_color = PBack.lightred
            else:
                raise ValueError('Invalid cell terrain while printing state key.')
            name = Terrains(terrain_index).name
            state_key_string += PBack.blue + '**||' + PBack.reset + \
                                cell_color + ''.center(10) + \
                                PBack.blue + '||' + PBack.reset + \
                                name.center(15) + \
                                PBack.blue + '||**' + PBack.reset + '\n'

        for mapobject_index in range(len(MapObjects)):
            if MapObjects(mapobject_index) == MapObjects.none:
                cell_val = '?'
            elif MapObjects(mapobject_index) == MapObjects.player:
                cell_val = '<,>,^,v'
            elif MapObjects(mapobject_index) == MapObjects.battery:
                cell_val = 'B'
            elif MapObjects(mapobject_index) == MapObjects.injured:
                cell_val = 'I'
            elif MapObjects(mapobject_index) == MapObjects.pedestrian:
                cell_val = 'P'
            elif MapObjects(mapobject_index) == MapObjects.zombie:
                cell_val = 'Z'
            else:
                raise ValueError('Invalid cell MapObject while printing state key.')
            name = MapObjects(mapobject_index).name
            state_key_string += PBack.blue + '**||' + PBack.reset + \
                                cell_val.center(10) + \
                                PBack.blue + '||' + PBack.reset + \
                                name.center(15) + \
                                PBack.blue + '||**' + PBack.reset + '\n'

        state_key_string += PBack.blue + buffer + PBack.reset

        print(state_key_string)
        return state_key_string


if __name__ == '__main__':
    # Quick Demo of class
    my_sgw = SGW()  # Set up
    my_sgw.play_type = PlayTypes.machine
    my_sgw.render_mode = PlayTypes.machine
    my_sgw.max_energy = 50
    my_sgw.map_file = None
    my_sgw.rand_profile = MapProfiles.trolley
    my_sgw.num_rows = 20
    my_sgw.num_cols = 20

    # Select an action (human or from agent)
    my_sgw.print_player_action_selections()
    action_selection = Actions.step_forward

    # Execute and advance the game
    new_obs, new_score, game_over, turn_info = my_sgw.step(raw_action=action_selection)

    # Render for a human
    my_sgw.print_state_key()
    my_sgw.render(mode=PlayTypes.human)
