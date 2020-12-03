import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional, cast
from zipfile import ZipFile

import click

from mcc.config import Config
from mcc.mcunit import McUnit

download_page = "https://www.minecraft.net/en-us/download/server"

@click.group(invoke_without_command=True)
@click.option("--debug/--no-debug", default=False)
@click.version_option()
@click.pass_context
def mcc(ctx, debug: bool):
    """Minecraft Control for minecraft servers"""

    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug

    if ctx.invoked_subcommand is None:
        click.echo("\nMinecraft Servers' State")
        click.echo(list())


def list():
    mc_units = McUnit.discover_units()

    result = ""
    result += f"{McUnit.heading}\n"
    for mc in mc_units:
        result += f"{repr(mc)}\n"
    return result


def list_worlds(mc_unit: McUnit):
    result = ""
    for i, world in enumerate(mc_unit.worlds):
        result += f" {i}={world}\n"
    return result


def server_command(
    wrapped: Callable[[McUnit, Any], None]
) -> Callable[[int, Any], None]:
    """
    a decorator that adds the server number argument to the command and validates
    that argument. It passes the McUnit object for the server to the wrapped function.
    Supports other click.arguments declared before @server_command, these are passed
    unchanged to the wrapped function

    Args:
        wrapped (Callable[[McUnit], None]): The function to be wrapped

    Returns:
        [type]: (Callable[[int], None]): The wrapped function
    """

    @wraps(wrapped)
    @mcc.command(name=wrapped.__name__)
    @click.argument("server", type=int, default=None, required=False)
    def wrapper(server: Optional[int], **kwargs):
        if server is None:
            server = click.prompt(f"which server?\n{list()}", type=int)
        server_num = cast(int, server)
        mc_unit = validate_server_num(server_num)
        wrapped(mc_unit, **kwargs)

    return wrapper


def validate_server_num(server: int) -> McUnit:
    mc_units = McUnit.discover_units()
    max = len(mc_units) - 1
    if server > max or server < 0:
        raise click.ClickException(f"please choose a server number between 0 and {max}")
    unit = mc_units[server]

    return unit


def validate_world_num(unit: McUnit, world: int):
    if world is None:
        world = click.prompt(f"which world?\n{list_worlds(unit)}", type=int)

    max_world = len(unit.worlds) - 1
    if world > max_world:
        raise click.ClickException(
            f"worlds for {unit.name} must be between 0 and {max_world}"
        )

    return world


@server_command
def console(mc_unit: McUnit):
    # mc_unit = validate_server_num(server)[server]
    click.echo("to be implemented ...")


@server_command
def stop(mc_unit: McUnit):
    click.echo(f"stopping server {mc_unit.name} ...")
    mc_unit.stop()
    list()


@server_command
def start(mc_unit: McUnit):
    click.echo(f"starting server {mc_unit.name} ...")
    mc_unit.start()
    list()


@server_command
def disable(mc_unit: McUnit):
    click.echo(f"disabling server {mc_unit.name} ...")
    mc_unit.disable()
    list()


@server_command
def enable(mc_unit: McUnit):
    click.echo(f"enabling server {mc_unit.name} ...")
    mc_unit.enable()
    list()


@server_command
def worlds(mc_unit: McUnit):
    click.echo(f"Worlds for server {mc_unit.name}:")
    click.echo(list_worlds(mc_unit))


@click.argument("world", type=int, default=None, required=False)
@server_command
def backup(mc_unit: McUnit, world: Optional[int]):
    world = validate_world_num(mc_unit, world)

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


@click.argument("world", type=int, default=None, required=False)
@server_command
def switch(mc_unit: McUnit, world: Optional[int]):
    world = validate_world_num(mc_unit, world)

    click.echo(f"Switching server {mc_unit.name} to World {mc_unit.worlds[world]}")

    mc_unit.set_world(world)
