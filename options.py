class Option:
    def __init__(self, name, command_string):
        self.name = name
        self.command_string = command_string
    
    def __str__(self) -> str:
        return "Option({}: {})".format(self.name, self.command_string)

class EnvironmentVariable(Option):
    def __init__(self, name, value):
        super().__init__(name, value)

class Strategy(Option):
    def __init__(self, type):
        self.check(type)
        super().__init__('Strategy', "-P {}".format(type))
    
    def check(self, type):
        types = ['explore', 'exploit']
        if type not in types:
            raise ValueError('Invalid strategy type')

class Schedule(Option):
    def __init__(self, type):
        self.check(type)
        super().__init__('Schedule', "-p {}".format(type))
    
    def check(self, type):
        types = ['explore', 'coe', 'lin', 'quad', 'exploit', 'rare']
        if type not in types:
            raise ValueError('Invalid schedule type')

class MutatorType(Option):
    def __init__(self, type):
        self.check(type)
        super().__init__('Mutator type', "-a {}".format(type))
    
    def check(self, type):
        types = ['ascii', 'binary']
        if type not in types:
            raise ValueError('Invalid mutator type')

class DisableTrimming(EnvironmentVariable):
    def __init__(self):
        super().__init__('Disable trimming', 'AFL_DISABLE_TRIM=true')

class OldQueueCycling(Option):
    def __init__(self):
        super().__init__('Old queue cycling', '-Z')
    
class  MOptMutator(Option):
    def __init__(self):
        super().__init__('MOpt mutator', '-L 0')