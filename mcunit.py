
import os
import configparser
from pathlib import Path
from time import sleep
from pystemd.systemd1 import Unit, Manager
from config import Config


class McUnit:
    """
    A class to represent a Unit of the minecraft service.
    The factory function discover_units expects to find installations of
    Minecraft Server in folders under /opt/minecraft and returns a list
    of McUnit
    """

    repr_format = "{:2s}  {:40s}{:15s}{:15s}{:12s}{:12s}{:20s}{:3s}"
    heading = repr_format.format(
        "No", "Name", "State", "SubState", "Auto Start", "GameMode", "World", "Worlds"
    )
    config_name = "server.properties"

    manager = Manager()
    manager.load()
    parser = configparser.ConfigParser()

    def __init__(self, name, unit, unit_name, num):
        self.name = name
        self.unit = unit
        self.unit_name = unit_name
        self.num = num
        self.config_path = Config.mc_root / name / self.config_name
        try:
            with open(self.config_path) as stream:
                self.parser.read_string("[top]\n" + stream.read())
            self.world = self.parser["top"]["level-name"]
            self.mode = self.parser["top"]["gamemode"]
        except (FileNotFoundError, KeyError):
            self.world = "Unknown"
            self.mode = "Unknown"
        self.worlds = [
            f.name
            for f in (Config.mc_root / name).iterdir()
            if f.name not in Config.non_worlds and f.is_dir()
        ]

    @classmethod
    def discover_units(cls):
        # factory function that queries systemd files and returns a list
        # of McUints (1 systemd unit per Minecraft installation)
        mc_installs = list(Config.mc_root.glob("*"))
        mc_names = [
            str(mc.name) for mc in mc_installs if not str(mc.name).startswith(".")
        ]

        units = []
        for i, mc_name in enumerate(mc_names):
            unit_name = Config.unit_name_format.format(mc_name)
            unit = Unit(unit_name.encode("utf8"))
            unit.load()
            units.append(McUnit(mc_name, unit, unit_name, i))

        return units

    def __repr__(self):
        state = self.unit.Unit.ActiveState.decode("utf8")
        sub_state = self.unit.Unit.SubState.decode("utf8")
        enabled = self.manager.Manager.GetUnitFileState(self.unit_name).decode()
        return self.repr_format.format(
            str(self.num),
            self.name,
            state,
            sub_state,
            enabled,
            self.mode,
            self.world,
            str(len(self.worlds)),
        )

    def set_world(self, world_num):
        if len(self.worlds) >= world_num >= 0:
            #self.stop()
            sleep(3)  # todo should really monitor state

            with open(self.config_path) as stream:
                self.parser.read_string("[top]\n" + stream.read())
            self.parser["top"]["level-name"] = self.worlds[world_num]
            contents = ""
            # is the best we can do with ConfigParser and a no sections file?
            for name, val in self.parser['top'].items():
                contents += f"{name}={val}\n"
            print(contents)


    def start(self):
        print(f"Starting {self.name} ...")
        self.unit.Start(b"replace")

    def stop(self):
        print(f"Stopping {self.name} ...")
        self.unit.Stop(b"replace")

    def restart(self):
        print(f"Restarting {self.name} ...")
        # unit.Restart does not work for some reason
        self.unit.Stop(b"replace")
        self.unit.Start(b"replace")

    def enable(self):
        self.manager.Manager.EnableUnitFiles([self.unit_name], False, False)

    def disable(self):
        self.manager.Manager.DisableUnitFiles([self.unit_name], False)

    def console(self):
        cmd = Config.screen_cmd_format.format(self.name)
        os.system(cmd)

    actions = {
        "s": start,
        "k": stop,
        "e": enable,
        "d": disable,
        "r": restart,
        "c": console,
    }
