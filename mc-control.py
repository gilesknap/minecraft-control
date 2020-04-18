import sys
import configparser
from pathlib import Path
from pystemd.systemd1 import Unit, Manager
from elevate import elevate


elevate(graphical=False)  # need sudo for systemd actions


class McUnit:
    """
    A class to represent a Unit of the minecraft service.
    The factory function discover_units expects to find installations of
    Minecraft Server in folders under /opt/minecraft and returns a list
    of McUnit
    """

    mc_root = Path("/opt/minecraft")
    unit_name_format = "minecraft@{}.service"
    config_name = "server.properties"
    repr_format = "{:2s}  {:40s}{:15s}{:15s}{:12s}{:12s}{:20s}"
    heading = repr_format.format(
        "No", "Name", "State", "SubState", "Auto Start", "GameMode", "World"
    )

    manager = Manager()
    manager.load()
    parser = configparser.ConfigParser()

    def __init__(self, name, unit, unit_name, num):
        self.name = name
        self.unit = unit
        self.unit_name = unit_name
        self.num = num
        self.config_path = self.mc_root / name / self.config_name
        try:
            with open(self.config_path) as stream:
                self.parser.read_string("[top]\n" + stream.read())
            self.world = self.parser["top"]["level-name"]
            self.mode = self.parser["top"]["gamemode"]
        except (FileNotFoundError, KeyError):
            self.world = "Unknown"
            self.mode = "Unknown"

    @classmethod
    def discover_units(cls):
        # factory function that queries systemd files and returns a list
        # of McUints (1 systemd unit per Minecraft installation)
        mc_installs = list(cls.mc_root.glob("*"))
        mc_names = [
            str(mc.name) for mc in mc_installs if not str(mc.name).startswith(".")
        ]

        units = []
        for i, mc_name in enumerate(mc_names):
            unit_name = cls.unit_name_format.format(mc_name)
            unit = Unit(unit_name.encode("utf8"))
            unit.load()
            units.append(McUnit(mc_name, unit, unit_name, i))

        return units

    def __repr__(self):
        state = self.unit.Unit.ActiveState.decode("utf8")
        sub_state = self.unit.Unit.SubState.decode("utf8")
        enabled = self.manager.Manager.GetUnitFileState(self.unit_name).decode()
        return self.repr_format.format(
            str(self.num), self.name, state, sub_state, enabled, self.mode, self.world,
        )

    def start(self):
        print(f"Starting {self.name} ...")
        self.unit.Start(b"replace")

    def stop(self):
        print(f"Stopping {self.name} ...")
        self.unit.Stop(b"replace")

    def restart(self):
        print(f"Restarting {self.name} ...")
        self.unit.Restart(b"replace")

    def enable(self):
        self.manager.Manager.EnableUnitFiles([self.unit_name], False, False)

    def disable(self):
        self.manager.Manager.DisableUnitFiles([self.unit_name], False)

    actions = {"s": start, "k": stop, "e": enable, "d": disable}


mc_units = McUnit.discover_units()


def show_state():
    print("\nMinecraft Servers' State")
    print(McUnit.heading)
    for i, mc in enumerate(mc_units):
        print(mc)


def choose_server():
    while True:
        print("\nChoose a Server (a=all <enter>=exit)?")
        response = sys.stdin.readline().strip("\n")
        if not response:
            break
        elif response == "a":
            return mc_units
        else:
            try:
                i = int(response)
                if i <= len(mc_units):
                    return [mc_units[i]]
            except ValueError:
                print("invalid entry")


def choose_action():
    while True:
        print("\nChoose an action" "(s=start k=stop e=enable d=disable <enter>=exit")
        response = sys.stdin.readline().strip("\n")
        if not response:
            break
        elif response in McUnit.actions:
            return McUnit.actions[response]
        else:
            print("invalid entry")


# main loop. Print status and request actions
while True:
    show_state()
    servers = choose_server()
    if not servers:
        break
    action = choose_action()
    if not action:
        break

    for server in servers:
        action(server)
