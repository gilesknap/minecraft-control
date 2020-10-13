import click

from mcc import __version__


@click.command()
def mcc():
    """Main Entry Point"""
    click.echo(f"version: {__version__}")