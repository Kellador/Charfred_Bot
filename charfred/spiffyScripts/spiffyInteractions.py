#!/usr/bin/env python

import click
from spiffyUtils import isUp, sendCmd


@click.group()
async def whitelist():
    pass


@whitelist.command()
@whitelist.argument('player')
async def add(player: str):
    """Whitelists a player."""
    True


@whitelist.command()
@whitelist.argument('player')
async def remove(player: str):
    """Removes a player from whitelist."""
    True


@whitelist.command()
@whitelist.argument('player')
async def check(player: str):
    """Checks whether a player is whitelisted or not."""
    True


@click.command()
@click.argument('player')
async def kick(player: str):
    """Kicks a player."""
    True


@click.command()
@click.argument('player')
async def ban(player: str):
    """Bans a player and removes him/her from the whitelist."""
    True


@click.command()
@click.argument('player')
@click.argument('rank')
async def promote(player: str, rank: str):
    """Promotes a player to the given rank."""
    True


@click.command()
@click.argument('player')
@click.argument('rank')
async def demote(player: str, rank: str):
    """Demotes a player to the given rank."""
    True


@click.command()
@click.argument('server')
@click.argument('command')
async def passThrough(server: str, command: str):
    """Passes a command to the given server's screen."""
    True


if __name__ == '__main__':
    # TODO: Implement standalone use with click.
    True
