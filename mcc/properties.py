from pathlib import Path
import configparser


class Properties:
    """
    A class to read/write from a properties file which but with no
    section headers (i.e. Minecraft's server.properties)
    """
    parser = configparser.ConfigParser()

    def __init__(self, filepath: Path):
        self.path: Path = filepath
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        self.dict: dict = {}

    def __getitem__(self, i):
        return self.dict.get(i)

    def __setitem__(self, i, val):
        if i in self.dict:
            self.dict[i] = val

    def read(self):
        # prepend a dummy 'top' section for ConfigParser
        with open(self.path) as stream:
            self.parser.read_string("[top]\n" + stream.read())
        self.dict = self.parser['top']

    def write(self):
        contents = ''
        for name, val in self.dict.items():
            contents += f"{name}={val}\n"

        with open(self.path, "w") as stream:
            stream.writelines(contents)
