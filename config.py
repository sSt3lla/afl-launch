from argparse import Namespace
import tomllib

class Config:
    def __init__(self, args: Namespace):
        self.input = args.i
        self.memory = args.m
        self.instances = args.n
        self.name = args.name
        self.no_master = args.no_master
        self.output = args.o
        self.timeout = args.t
        self.dict = args.x
        self.config = args.c
        self.config_data = self.load_config()

    def load_config(self):
        with open(self.config) as f:
            return tomllib.loads(f.read())