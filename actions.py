import os
import random
from math import ceil
from config import Config
from options import Strategy, Schedule, MutatorType, DisableTrimming, OldQueueCycling, MOptMutator, Option, EnvironmentVariable

#We have a config that we need to then turn into what we need the actions to do


class Actions:
    def __init__(self, config: Config):
        self.config = config

        if self.config.instances == 0:
            self.config.instances = len(os.sched_getaffinity(0))
        self.instances:list[Instance] = []

        self.power_schedule = self.setup_power_schedule()
        self.secondary_options = self.setup_secondary_options()

        self.setup_instances()

    def setup_power_schedule(self):
        power_schedule = []
        strategies = ['explore', 'coe', 'lin', 'quad', 'exploit', 'rare']


        for strategy in strategies:
            count = int(self.config.config_data['power_schedule'][strategy])
            power_schedule.extend([Schedule(strategy) for _ in range(count)])
        
        assert len(power_schedule) < self.config.instances, "Power schedule values exceed the number of instances"
        return power_schedule
        
    def setup_secondary_options(self):
        secondary_options = []
        option_table : dict[str, Option] = {
            'MOpt_mutator': MOptMutator(),
            'old_queue_cycle': OldQueueCycling(),
            'disable_trimming': DisableTrimming(),
            'explore_strategy': Strategy('explore'),
            'exploit_strategy': Strategy('exploit'),
            'ascii_type': MutatorType('ascii'),
            'binary_type': MutatorType('binary')
        }

        for option, obj in option_table.items():
            count = ceil(self.config.config_data['secondary_options'][option] * self.config.instances)
            count = max(0, count)
            secondary_options.append([obj for _ in range(count)])
        return secondary_options

    def setup_instances(self):
        random_power_schedule = self.power_schedule.copy()
        random_power_schedule.extend([None] * (self.config.instances - len(random_power_schedule)))
        random.shuffle(random_power_schedule)


        random_secondary_options = []
        # Create a copy of secondary_options to avoid modifying the originala
        for options in self.secondary_options:
            options_copy = options.copy()
            options_copy.extend([None] * (self.config.instances - len(options_copy)))
            random.shuffle(options_copy)
            random_secondary_options.append(options_copy)

        for _ in range(self.config.instances):
            power_schedule = random_power_schedule.pop()
            secondary_option = [option.pop() for option in random_secondary_options]
        

            new_instance = Instance(self.config.input, 
                                    self.config.output, 
                                    memory=self.config.memory, 
                                    timeout=self.config.timeout, 
                                    dict=self.config.dict, 
                                    power_schedule=power_schedule,
                                    secondary_options=secondary_option)
            self.instances.append(new_instance)

class Instance:
    start_command = "afl-fuzz -i {} -m {} -o {} -t {}"

    def __init__(self, input, output, memory='0', timeout='+', dict=None, power_schedule=None, secondary_options=None):
        self.input = input
        self.output = output
        self.memory = memory
        self.timeout = timeout
        self.dict = dict
        self.power_schedule = power_schedule
        self.secondary_options = [option for option in secondary_options if option]
    
    def get_command(self) -> str:

        def flatten(_list):
            return [i for xs in _list for i in xs]

        command = []
        env = []
        for option in self.secondary_options:
            if option:
                if isinstance(option, EnvironmentVariable):
                    env.append(option.command_string)
                else:
                    command.append(option.command_string)
        
        env_joined = ' '.join(env)
        if env_joined:
            env_joined += ' '

        command_joined = ' '.join(command)

        afl_command = Instance.start_command.format(self.input, self.memory, self.output, self.timeout)
        if afl_command:
            afl_command += ' '


        return env_joined + afl_command + command_joined