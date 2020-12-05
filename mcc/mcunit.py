import os
from pathlib import Path
from time import sleep
from typing import List

from pystemd.dbuslib import DBus
from pystemd.systemd1 import Manager, Unit

from mcc.config import Config
from mcc.properties import Properties


class McUnit:
    """
    A class to represent a Unit of the minecraft service.
    The factory function discover_units expects to find installations of
    Minecraft Server in folders under /home/{user}/MinecraftServers
    and returns a list of McUnit
    """

    repr_format = "{:3.2s}{:20.19s}{:11.10s}{:8.7s}{:9.8s}{:10.9s}{:15.14s}{:4.4s}"
    heading = repr_format.format(
        "No", "Name", "State", "SubSt", "Auto Start", "GameMode", "World", "Wlds"
    )
    config_name = "server.properties"

    # keep a dbus and a manager for the lifetime of the class/app
    dbus = DBus(user_mode=True)
    dbus.open()
    manager = Manager(bus=dbus)
    manager.load()

    def __init__(self, name, unit, unit_name, num):
        self.name = name
        self.unit = unit
        self.unit_name = unit_name
        self.num = num
        self.config_path = Config.mc_root / name / self.config_name

        self.properties = Properties(self.config_path)
        self.properties.read()
        self.world = self.properties["level-name"]
        self.mode = self.properties["gamemode"]

        self.worlds = [
            f.name
            for f in (Config.mc_root / name).iterdir()
            if f.name not in Config.non_worlds and f.is_dir()
        ]

    @classmethod
    def discover_units(cls) -> List["McUnit"]:
        # factory function that queries systemd files and returns a list
        # of McUints (1 systemd unit per Minecraft installation)

        # find all directories off of root that contain server.properties
        units = []
        glob_path = str(Path("*") / "server.properties")
        for i, props in enumerate(Config.mc_root.glob(glob_path)):
            mc_name = str(props.parent.stem)
            unit_name = Config.unit_name_format.format(mc_name)
            unit = Unit(unit_name.encode("utf8"), bus=cls.dbus)
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

    def get_world_path(self, world_num):
        if not len(self.worlds) >= world_num >= 0:
            raise ValueError(f"world number {world_num} does not exist")
        return Config.mc_root / self.name / self.worlds[world_num]

    def set_world(self, world_num):
        self.properties.read()
        if not len(self.worlds) >= world_num >= 0:
            raise ValueError(f"world number {world_num} does not exist")

        self.properties["level-name"] = self.worlds[world_num]
        self.properties.write()
        self.world = self.worlds[world_num]

    def start(self):
        self.unit.Start(b"replace")

    def stop(self):
        self.unit.Stop(b"replace")

        # wait for the service to complete termination
        while self.running:
            sleep(0.2)

    def restart(self):
        # unit.Restart does not work for some reason
        self.stop()
        self.start()

    def enable(self):
        self.manager.Manager.EnableUnitFiles([self.unit_name], False, False)

    def disable(self):
        self.manager.Manager.DisableUnitFiles([self.unit_name], False)

    def console(self):
        cmd = Config.screen_cmd_format.format(self.name)
        os.system(cmd)

    @property
    def running(self):
        state = self.unit.Unit.ActiveState.decode("utf8")
        return state != "inactive"
