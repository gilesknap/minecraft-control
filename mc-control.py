import sys
from pathlib import Path
from pystemd.systemd1 import Unit, Manager
from elevate import elevate


class McUnit:
    mc_root = Path('/opt/minecraft')
    unit_name_format = 'minecraft@{}.service'
    systemd_enabled_format = '/etc/systemd/system/multi-user.target.wants/{}'

    def __init__(self, name, num, unit, path):
        self.name = name
        self.num = num
        self.unit = unit
        self.path = path

    @classmethod
    def discover_units(cls):
        # factory function that queries systemd files and returns a dictionary
        # of McUints (1 systemd unit per Minecraft installation)
        mc_installs = list(cls.mc_root.glob('*'))
        mc_names = [
            str(mc.name) for mc in mc_installs if
            not str(mc.name).startswith('.')
        ]

        units = {}
        for i, mc_name in enumerate(mc_names):
            unit_name = cls.unit_name_format.format(mc_name)
            unit = Unit(unit_name.encode("utf8"))
            unit.load()
            path = Path(cls.systemd_enabled_format.format(unit_name))
            units[i] = McUnit(mc_name, i, unit, path)

        return units


def start(num):
    print(f"Starting {mc_units[num].name} ...")
    mc_units[num].unit.Start(b'replace')


def stop(num):
    print(f"Stopping {mc_units[num].name} ...")
    mc_units[num].unit.Stop(b'replace')


def enable(name):
    pass


def disable(name):
    pass


actions = {
    "s": start,
    "k": stop,
    "e": enable,
    "d": disable
}


mc_units = McUnit.discover_units()


def show_state():
    print("\nMinecraft Servers' State")
    print("No. {:40s}{:15s}{:15s}{}".format(
        "Name", "State", "SubState", "Auto Start"
    ))
    for i, mc in enumerate(mc_units.values()):
        state = mc.unit.Unit.ActiveState.decode("utf8")
        sub_state = mc.unit.Unit.SubState.decode("utf8")
        enabled = mc.path.exists()
        print(f"{i:2d}  {mc.name:40s}{state:15s}{sub_state:15s}{enabled}")


def choose_server():
    while True:
        print("which server do you want to change (a=all <enter>=exit)?")
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
        print("which action (s=start k=stop e=enable d=disable <enter>=exit")
        response = sys.stdin.readline().strip("\n")
        if not response:
            break
        elif response in actions:
            return actions[response]
        else:
            print("invalid entry")


elevate(graphical=False)

manager = Manager()
manager.load()
man_units = manager.Manager.ListUnitFiles()
for name, enabled in man_units:
    str_name = name.decode()
    if "minecraft" in str_name:
        print(str_name, enabled)

while True:
    show_state()
    servers = choose_server()
    if not servers:
        break
    action = choose_action()
    if not action:
        break

    for server in servers:
        print(action, server.name)
        action(server.num)
