import os
from datetime import datetime
from typing import List
from zipfile import ZipFile

import click

from mcc import __version__
from mcc.config import Config
from mcc.mcunit import McUnit


@click.group(invoke_without_command=True)
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def mcc(ctx, debug: bool):
    """Minecraft Control for minecraft servers"""
    click.echo(f"minecraft-control version: {__version__}\n")

    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug

    if ctx.invoked_subcommand is None:
        list(None)


@mcc.resultcallback()
def list(result, **kwargs):
    mc_units = McUnit.discover_units()

    click.echo("\nMinecraft Servers' State")
    click.echo(McUnit.heading)
    for mc in mc_units:
        click.echo(mc)


def validate_server_num(server: int, world: int = 0) -> List[McUnit]:
    mc_units = McUnit.discover_units()
    max = len(mc_units) - 1
    if server > max or server < 0:
        raise click.ClickException(f"please choose a server number between 0 and {max}")
    unit = mc_units[server]
    max_world = len(unit.worlds)
    if world > max_world:
        raise click.ClickException(
            f"worlds for {unit.name} must be between 0 and {max_world}"
        )
    return mc_units


@click.argument("server", type=int)
@mcc.command()
def console(server: int):
    # mc_unit = validate_server_num(server)[server]
    click.echo("to be implemented ...")


@click.argument("server", type=int)
@mcc.command()
def stop(server: int):
    mc_unit = validate_server_num(server)[server]
    click.echo(f"stopping server {mc_unit.name} ...")
    mc_unit.stop()


@click.argument("server", type=int)
@mcc.command()
def start(server: int):
    mc_unit = validate_server_num(server)[server]
    click.echo(f"starting server {mc_unit.name} ...")
    mc_unit.start()


@click.argument("server", type=int)
@mcc.command()
def disable(server: int):
    mc_unit = validate_server_num(server)[server]
    click.echo(f"disabling server {mc_unit.name} ...")
    mc_unit.disable()


@click.argument("server", type=int)
@mcc.command()
def enable(server: int):
    mc_unit = validate_server_num(server)[server]
    click.echo(f"enabling server {mc_unit.name} ...")
    mc_unit.enable()


@click.argument("server", type=int)
@mcc.command()
def worlds(server: int):
    mc_unit = validate_server_num(server)[server]

    click.echo(f"Worlds for server {mc_unit.name}:")
    for i, world in enumerate(mc_unit.worlds):
        click.echo(f" {i}={world}")


@click.argument("world", type=int)
@click.argument("server", type=int)
@mcc.command()
def switch(server: int, world: int):
    mc_unit = validate_server_num(server, world)[server]
    click.echo(f"Switching server {mc_unit.name} to World {mc_unit.worlds[world]}")
    mc_unit.set_world(world)


@click.argument("world", type=int)
@mcc.command()
def backup(server: int, world: int):
    mc_unit = validate_server_num(server, world)[server]
    click.echo(f"backing up server {mc_unit.name} ...")

    world_name = mc_unit.worlds[world]
    d = datetime.today().strftime("%Y-%m-%d")
    fname = f"{d}.{mc_unit.name}.{world_name}.zip"
    dest = Config.backup_path / fname
    w_path = mc_unit.get_world_path(world)
    click.echo(f"Backing up {w_path} to {dest}")

    with ZipFile(dest, "w") as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(w_path):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                zipObj.write(filePath)
