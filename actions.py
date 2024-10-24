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
        
            new_instance = Instance(self.config.binary_path,
                                    self.config.input, 
                                    self.config.output, 
                                    secondary_options,
                                    i,
                                    self.config.name,
                                    self.config.memory,
                                    self.config.timeout,
                                    self.config.dict)
            
            instances.append(new_instance)

        return instances
    
    def get_names_and_commands(self) -> dict[str, str]:
        commands = {}
        for instance in self.instances:
            commands[instance.fuzzer_name] = instance.get_command()
        return commands

class Instance:
    def __init__(self, binary_path, input, output, secondary_options: list[Option], count, name=None, memory=0, timeout="'+'", dict=None):
        self.binary_path = binary_path
        self.input = input
        self.output = output
        self.secondary_options = secondary_options
        self.count = count
        if self.count == 0:
            self.main = True
        else:
            self.main = False
        self.name = str(name)
        self.memory = memory
        self.timeout = str(timeout)
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


        name = ''
        if self.name != 'None':
            name = '-' + self.name
        if self.main:
            self.fuzzer_name = 'main' + name
            fuzzer_command_name = '-M main' + name
        else:
            self.fuzzer_name = 'secondary' + name + '-' + str(self.count)
            fuzzer_command_name = '-S secondary' + name + '-' + str(self.count)

        afl_command = f"{env_joined}afl-fuzz {fuzzer_command_name} -i {self.input} -o {self.output}"
        if self.memory:
            afl_command += f" -m {self.memory}"
        if self.timeout is None:
            afl_command += f" -t {self.timeout}"
        if self.dict:
            afl_command += f" -x {self.dict}"

        afl_command += ' ' + command_joined
        afl_command += f"-- {self.binary_path} -"
        return afl_command