import os
import argparse
from SGWMachineTrain import SGW
from gym_sgw.envs.enums.Enums import MapProfiles

parser = argparse.ArgumentParser(description='CLI Argument Parser for RL Training.')
parser.add_argument('--modelfilename', help='Output file name for learned model.', default='rl-agent-test')
parser.add_argument('--logpath', help='Data logging file path.', default='./logs')
parser.add_argument('--creation', help='Allow creation of output file.', default=True, action='store_true')
parser.add_argument('--training_steps', help='Number of steps to train for.', type=int, default=10000)


def validate_data(out_dirs, allow_creation=False):
    for out_dir in out_dirs:
        if allow_creation and not os.path.exists(out_dir):
            os.mkdir(out_dir)
        if not os.path.isdir(out_dir):
            raise EnvironmentError('Bad path provided in CLI arguments.')


if __name__ == '__main__':

    # Parse CLI Args
    args = parser.parse_args()
    os.system('mode con: cols=125 lines=62')
    validate_data([args.logpath], allow_creation=args.creation)

    # Set runtime args
    model_filename = args.modelfilename
    data_log_path = args.logpath
    training_steps = args.training_steps
    max_energy = 50
    rand_prof = MapProfiles.trolley
    num_rows = 25
    num_cols = 25

    # Create and run game with those params
    sgw_env = SGW(
        model_filename=model_filename,
        data_log_path=data_log_path,
        training_steps=training_steps,
        max_turns=200,
        max_energy=50,
        rand_prof=MapProfiles.trolley,
        num_rows=25,
        num_cols=25
    )
    sgw_env.run()
