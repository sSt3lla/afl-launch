import random
from config import Config
from options import EnvironmentVariable, Option
from typing import Optional, Sequence

#We have a config that we need to then turn into what we need the actions to do


class Actions:
    def __init__(self, config: Config):
        self.config = config
        self.instances = self.setup_instances()

    def setup_instances(self):
        instances: list['Instance'] = []

        # Full options containing None values so we get an even distribution
        full_secondary_options: list[list[Optional[Option]]] = []
        for option in self.config.secondary_options:
            option_copy = option.copy()
            option_copy.extend([None] * (self.config.instances - len(option)))

            random.shuffle(option_copy)
            full_secondary_options.append(option_copy)

        # Create instances by popping the last value from each option and only adding if it's not None
        for i in range(self.config.instances):
            secondary_options = []
            for option in full_secondary_options:
                option_value = option.pop()
                if option_value:
                    secondary_options.append(option_value)

            # If we don't want a master instance, we skip the first one
            if self.config.no_master:
                i += 1
        
            new_instance = Instance(self.config.input, 
                                    self.config.output, 
                                    secondary_options,
                                    i,
                                    self.config.memory,
                                    self.config.timeout,
                                    self.config.dict)
            
            instances.append(new_instance)

        return instances

class Instance:
    start_command = "afl-fuzz {} -i {} -o {}"
    def __init__(self, input, output, secondary_options: list[Option], count, name=None, memory='0', timeout="'+'", dict=None):
        self.input = input
        self.output = output
        self.secondary_options = secondary_options
        self.count = count
        if self.count == 0:
            self.main = True
        else:
            self.main = False
        self.name = name
        self.memory = memory
        self.timeout = timeout
        self.dict = dict
    
    def get_command(self) -> str:
        command = []
        env = []
        for option in self.secondary_options:
            if option:
                if isinstance(option, EnvironmentVariable):
                    env.append(option.command_string)
                else:
                    command.append(option.command_string)
        
        env_joined = ' '.join(env) + ' ' if env else ''
        command_joined = ' '.join(command) + ' ' if command else ''
        name = self.name + '-' if self.name else ''
       

        if self.main:
            afl_fuzzer_name = '-M main' + name
        else:
            afl_fuzzer_name = '-S secondary' + name + '-' + str(self.count)


        afl_command = f"{env_joined}afl-fuzz {afl_fuzzer_name} -i {self.input} -o {self.output}"
        if self.memory:
            afl_command += f" -m {self.memory}"
        if self.timeout:
            afl_command += f" -t {self.timeout}"
        if self.dict:
            afl_command += f" -x {self.dict}"

        afl_command += ' ' + command_joined
        return afl_command