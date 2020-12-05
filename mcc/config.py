from os import environ
from pathlib import Path


class Config:
    # todo these should be read from a config file
    user = environ.get("USER")
    backup_path = Path("/mnt/bigdisk/MinecraftBackups")
    mc_root = Path(f"/home/{user}/MinecraftServers")
    unit_name_format = "minecraft@{}.service"
    screen_cmd_format = "/usr/bin/screen -Dr mc-{}"