from enum import IntEnum, Enum


class Terrains(IntEnum):
    none = 0
    out_of_bounds = 1
    wall = 2
    floor = 3
    future_fire = 4
    fire = 5
    hospital = 6


class MapObjects(IntEnum):
    none = 0
    injured = 1
    # zombie = 3
    battery = 4
    player = 5


class Actions(IntEnum):
    none = 0
    turn_left = 1
    turn_right = 2
    step_forward = 3


class Orientations(IntEnum):
    up = 0
    right = 1
    down = 2
    left = 3


class PlayTypes(IntEnum):
    human = 0
    machine = 1


class MapProfiles(IntEnum):
    uniform = 0
    trolley = 1
    sparse = 2
    pacman = 3
    spoiled = 4
    twisty = 5
    volcano = 6
    simple = 7


class MapColors(Enum):
    play_area = '#000000'
    game_screen = '#6665adff'
    black_tile = 'gym_sgw/envs/assets/sgai_terrain_outofbounds.png'
    wall_tile = "gym_sgw/envs/assets/sgai_terrain_impassable.png"
    floor_tile = 'gym_sgw/envs/assets/sgai_terrain_passable.png'
    future_fire_tile = "gym_sgw/envs/assets/sgai_fire_spreading.png"
    fire_tile = "gym_sgw/envs/assets/sgai_fire_regular.png"
    hospital_tile = "gym_sgw/envs/assets/sgai_hospital.png"
    battery = "gym_sgw/envs/assets/sgai_battery.png"
    ambulance_up = "gym_sgw/envs/assets/sgai_ambulance_up.png"
    ambulance_down = "gym_sgw/envs/assets/sgai_ambulance_down.png"
    ambulance_left = "gym_sgw/envs/assets/sgai_ambulance_left.png"
    ambulance_right = "gym_sgw/envs/assets/sgai_ambulance_right.png"
    text = '#000000'


class GameState(Enum):
    quit = -1
    title = 0
    new_game = 1
    close = 2


class SchemeColors(Enum):
    blue = (100, 143, 255)
    light_blue = (204, 218, 255)
    purple = (120, 94, 240)
    light_purple = (215, 207, 255)
    pink = (220, 38, 127)
    light_pink = (250, 190, 219)
    orange = (254, 97, 0)
    light_orange = (255, 194, 156)
    yellow = (255, 176, 0)
    white = (255, 255, 255)

