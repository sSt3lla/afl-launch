import pathlib
import shutil
import subprocess
import os
from typing import List

class CompileOption:
    def __init__(self, name: str, environment):
        self.name = name
        self.environment = environment

    def compile(self, source: pathlib.Path):
        os.chdir(source)
        file = pathlib.Path("afl-compile.sh")
        if not file.is_file():
            raise Exception("Source file not found")

        result = subprocess.run(["afl-compile.sh", self.name], env=self.environment)

        #
        
        # afl_image.run(
        #     "-ti",
        #     "-v",
        #     f"{self.source}:/src",
        #     "aflplusplus/aflplusplus",
        #     "afl-clang",
        #     "-o",
        #     f"/src/{self.name}",
        #     f"/src/{self.source.name}",
        #     env=self.environment,
        # )

        #docker run -ti -v .:/src aflplusplus/aflplusplus

compile_option: List[CompileOption] = []
compile_option.append(CompileOption("test", pathlib.Path("test"), {}))