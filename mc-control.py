import sys
from pathlib import Path
from pystemd.systemd1 import Unit
from elevate import elevate

systemd_enabled_format = '/etc/systemd/system/multi-user.target.wants/' \
    'minecraft@{}.service'
unit_format = 'minecraft@{}.service'
mc_root = Path('/opt/minecraft')
mc_installs = list(mc_root.glob('*'))
mc_names = [
    str(mc.name) for mc in mc_installs if not str(mc.name).startswith('.')
]
mc_units = {}
mc_paths = {}


def start(name):
    print(f"Starting {name} ...")
    mc_units[name].Start(b'replace')


def stop(name):
    print(f"Stopping {name} ...")
    mc_units[name].Stop(b'replace')


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


for mc in mc_names:
    unit_name = unit_format.format(mc)
    mc_units[mc] = Unit(unit_name.encode("utf8"))
    mc_units[mc].load()
    mc_paths[mc] = Path(systemd_enabled_format.format(mc))


def show_state():
    print("\nMinecraft Servers' State")
    print("No. {:40s}{:15s}{:15s}{}".format(
        "Name", "State", "SubState", "Auto Start"
    ))
    for i, mc in enumerate(mc_names):
        state = mc_units[mc].Unit.ActiveState.decode("utf8")
        sub_state = mc_units[mc].Unit.SubState.decode("utf8")
        enabled = mc_paths[mc].exists()
        print(f"{i:2d}  {mc:40s}{state:15s}{sub_state:15s}{enabled}")


def choose_server():
    while True:
        print("which server do you want to change (a=all <enter>=exit)?")
        response = sys.stdin.readline().strip("\n")
        if not response:
            break
        elif response == "a":
            return mc_names
        else:
            try:
                i = int(response)
                if i <= len(mc_names):
                    return [mc_names[i]]
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

while True:
    show_state()
    servers = choose_server()
    if not servers:
        break
    action = choose_action()
    if not action:
        break

    for server in servers:
        print(action, server)
        action(server)
