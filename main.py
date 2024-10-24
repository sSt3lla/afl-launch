import argparse
import pathlib
from config import Config
from actions import Actions
from random import seed
from tmux import run_commands

def main():
    parser = argparse.ArgumentParser(description='afl-big fuzzing tool options')

    parser.add_argument('binary_path', type=pathlib.Path, help='Path to the binary to fuzz')
    parser.add_argument('-i', type=pathlib.Path, required=True, help='afl-fuzz -i option (input location)')
    parser.add_argument('-m', type=int, default=0, help='afl-fuzz -m option (memory limit), 0 for no limit (defaults to 0)')
    parser.add_argument('-n', type=int, default=0, help='Number of instances to launch, 0 for automatic (defaults to 0)')
    parser.add_argument('-name', type=str, help='Base name for instances. Fuzzers will work in <output>/<BASE>-[Main|Secondary]-<N>')
    parser.add_argument('-no-master', default=False, action='store_true', help='Launch all instances with -S')
    parser.add_argument('-o', type=pathlib.Path, required=True, help='afl-fuzz -o option (output location)')
    parser.add_argument('-t', type=int, default=0, help='afl-fuzz -t option (timeout) (defaults to 0)')
    parser.add_argument('-x', type=pathlib.Path, help='afl-fuzz -x option (dict)')
    parser.add_argument('-c', type=pathlib.Path, default='fuzz.toml', help='Config file path (default to fuzz.toml)')

    seed(0)

    args = parser.parse_args()
    config = Config(args)
    actions = Actions(config)
    run_commands(actions.get_commands_and_names())

if __name__ == '__main__': 
    main()