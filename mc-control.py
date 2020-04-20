from zipfile import ZipFile
import os
from datetime import datetime
from time import sleep
from mcc.mcunit import McUnit
from mcc.config import Config

mc_units = McUnit.discover_units()


def show_state():
    print("\nMinecraft Servers' State")
    print(McUnit.heading)
    for mc in mc_units:
        print(mc)


def set_world(unit):
    chooser = Config.make_world_chooser(unit.worlds)
    world = chooser.ask()
    if world:
        print(f"switching to {world}")
        unit.set_world(int(world))
    else:
        print("cancelled")

def backup_world(unit):
    print("Warning, this will stop the server first. Press Enter to cancel")
    chooser = Config.make_world_chooser(unit.worlds)
    world = chooser.ask()
    if world:
        unit.stop()

        world_name = unit.worlds[int(world)]
        d = datetime.today().strftime('%Y-%m-%d')
        fname = f"{d}.{unit.name}.{world_name}.zip"
        dest = Config.backup_path / fname
        w_path = unit.get_world_path(int(world))
        print(f"Backing up {w_path} to {dest}")

        with ZipFile(dest, 'w') as zipObj:
            # Iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(w_path):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipObj.write(filePath)
    else:
        print("cancelled")


all_actions = McUnit.actions
all_actions.update({"w": set_world, "b": backup_world})
choose_server = Config.make_server_chooser(len(mc_units))
choose_action = Config.make_action_chooser(all_actions)


# main loop. Print status and request actions
while True:
    show_state()
    server = choose_server.ask()
    if not server:
        break
    action = choose_action.ask()
    if action:
        function = McUnit.actions[action]
        if server == "a":
            for unit in mc_units:
                function(unit)
        else:
            function(mc_units[int(server)])
    else:
        print("No action")
