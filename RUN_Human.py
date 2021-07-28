import os
import argparse
from SGWHumanPlay import SGW as SGWHuman
from SGWMachinePlay import SGW as SGWMachine
from gym_sgw.envs.enums.Enums import MapProfiles
import asyncio

parser = argparse.ArgumentParser(description='CLI Argument Parser for Human Play.')
parser.add_argument('--outfile', help='Data logging file name.', default='data_log_human.json')
parser.add_argument('--creation', help='Allow creation of output file.', default=True, action='store_true')
parser.add_argument('--games', help='Number of games to play. (machine mode only)', default='1')
parser.add_argument('--manual', help='Enables manual mode (machine mode only)', default=False, action='store_true')


def validate_data(out_file, allow_creation=False):
    if allow_creation and not os.path.exists(out_file):
        f = open(out_file, 'w+')
        f.close()
    if not os.path.isfile(out_file):
        raise EnvironmentError('Bad filename provided in CLI arguments.')

async def start_game(human_env, machine_env):
    await sgw_env_human.start(sgw_env_human, sgw_env_machine)

if __name__ == '__main__':

    # Parse CLI Args
    args = parser.parse_args()
    os.system('mode con: cols=125 lines=62')
    validate_data(args.outfile, allow_creation=args.creation)

    # Set runtime args
    data_log_file = args.outfile
    map_file = None  # None -> random map, map files have top priority
    max_energy = 50
    rand_prof = MapProfiles.concentrated
    num_rows = 20
    num_cols = 20

    # Create and run game with those params
    sgw_env_human = SGWHuman(
        data_log_file=data_log_file,
        map_file=map_file,
        max_energy=max_energy,
        rand_prof=rand_prof,
        num_rows=num_rows,
        num_cols=num_cols
    )
    sgw_env_machine = SGWMachine(
        data_log_file=data_log_file,
        map_file=map_file,
        max_energy=max_energy,
        rand_prof=rand_prof,
        num_rows=num_rows,
        num_cols=num_cols,
        manual=args.manual
    )
    asyncio.run(start_game(sgw_env_human, sgw_env_machine))
