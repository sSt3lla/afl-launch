import argparse
import pathlib
from config import Config
from actions import Actions

def main():
    parser = argparse.ArgumentParser(description='afl-big fuzzing tool options')

    parser.add_argument('-i', type=pathlib.Path, required=True, help='afl-fuzz -i option (input location)')
    parser.add_argument('-m', type=int, default=0, help='afl-fuzz -m option (memory limit), 0 for no limit (defaults to 0)')
    parser.add_argument('-n', type=int, default=0, help='Number of instances to launch, 0 for automatic (defaults to 0)')
    parser.add_argument('-name', type=str, help='Base name for instances. Fuzzers will work in <output>/<BASE>-[M|S]-<N>')
    parser.add_argument('-no-master', default=False, action='store_true', help='Launch all instances with -S')
    parser.add_argument('-o', type=pathlib.Path, required=True, help='afl-fuzz -o option (output location)')
    parser.add_argument('-t', type=int, default=0, help='afl-fuzz -t option (timeout) (defaults to 0)')
    parser.add_argument('-x', type=pathlib.Path, help='afl-fuzz -x option (dict)')
    parser.add_argument('-c', type=pathlib.Path, default='fuzz.toml', help='Config file path (default to fuzz.toml)')

    args = parser.parse_args()
    config = Config(args)
    actions = Actions(config)

    for instance in actions.instances:
        print(instance.get_command())

if __name__ == '__main__': 
    main()