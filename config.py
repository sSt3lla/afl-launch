from argparse import Namespace
import tomllib
from options import Strategy, Schedule, MutatorType, DisableTrimming, OldQueueCycling, MOptMutator, Option
from math import ceil
import os

class Config:
    def __init__(self, args: Namespace):
        self.input = args.i
        self.memory = args.m

        self.instances = args.n
        if self.instances == 0:
            self.instances = len(os.sched_getaffinity(0))

        self.name = args.name
        self.no_master = args.no_master
        self.output = args.o
        self.timeout: int | str = args.t
        if self.timeout == 0:
            self.timeout = '+'

        self.dict = args.x
        self.config_location = args.c
        self.config_data = self.load_config()
        self.secondary_options = self.setup_secondary_options() + [self.setup_power_schedule()]

    def setup_power_schedule(self):
        power_schedule = []
        strategies = ['explore', 'coe', 'lin', 'quad', 'exploit', 'rare']

        for strategy in strategies:
            count = int(self.config_data['power_schedule'][strategy])
            power_schedule.extend([Schedule(strategy) for _ in range(count)])
        
        assert len(power_schedule) < self.instances, 'Power schedule values exceed the number of instances'
        return power_schedule


    def setup_secondary_options(self):

        secondary_options: list[list[Option]] = []
        option_table : dict[str, Option] = {
            'MOpt_mutator': MOptMutator(),
            'old_queue_cycle': OldQueueCycling(),
            'disable_trimming': DisableTrimming(),
            'explore_strategy': Strategy('explore'),
            'exploit_strategy': Strategy('exploit'),
            'ascii_type': MutatorType('ascii'),
            'binary_type': MutatorType('binary')
        }

        strategies = []
        mutator_types = []

        for option, obj in option_table.items():
            count = ceil(self.config_data['secondary_options'][option] * self.instances)
            count = max(0, count)

            # Group Strategy and MutatorType into their respective lists
            if isinstance(obj, Strategy):
                strategies.extend([obj for _ in range(count)])
            elif isinstance(obj, MutatorType):
                mutator_types.extend([obj for _ in range(count)])
            else:
                secondary_options.append([obj for _ in range(count)])

        return secondary_options + [strategies, mutator_types]


    def load_config(self):
        with open(self.config_location) as f:
            return tomllib.loads(f.read())