import os
from datetime import datetime
from zipfile import ZipFile

import click

from mcc import __version__
from mcc.config import Config


@click.command()
def mcc():
    """Main Entry Point"""
    click.echo(f"version: {__version__}")


def set_world(unit):
    chooser = Config.make_world_chooser(unit.worlds)
    world = chooser.ask()
    if world:
        print(f"switching to {world}")
        unit.set_world(int(world))
        print("Please restart the server to see the new world")
    else:
        print("cancelled")


def backup_world(unit):
    print("Warning, this will stop the server first. Press Enter to cancel")
    chooser = Config.make_world_chooser(unit.worlds)
    world = chooser.ask()
    if world:
        unit.stop()

        world_name = unit.worlds[int(world)]
        d = datetime.today().strftime("%Y-%m-%d")
        fname = f"{d}.{unit.name}.{world_name}.zip"
        dest = Config.backup_path / fname
        w_path = unit.get_world_path(int(world))
        print(f"Backing up {w_path} to {dest}")

        with ZipFile(dest, "w") as zipObj:
            # Iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(w_path):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipObj.write(filePath)
    else:
        print("cancelled")

