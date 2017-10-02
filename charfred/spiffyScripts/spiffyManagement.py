#!/usr/bin/env python

import click
import asyncio
from spiffyUtils import isUp, sendCmd
import spiffyConfigs as cfg


@click.command()
@click.argument('server')
async def start(server: str):
    """Starts a server, if it is not running already."""
    if isUp(server):
        print(f'[INFO] {server} appears to be running already!')
    else:
        print(f'[INFO] Starting {server}')
        await asyncio.create_subprocess_exec(
            'screen', '-h', '5000', '-dmS', server,
            f'{cfg.serverspath}/{server}',
            cfg.servers[server]['Invocation'], 'nogui'
        )
        if isUp(server):
            print(f'[INFO] {server} is now running!')
        else:
            print(f'[WARNING] {server} does not appear to have started!')


@click.command()
@click.argument('server')
async def stop(server: str):
    """Stops a server, if it is currently running."""
    True


@click.command()
@click.argument('server')
async def restart(server: str):
    """Restarts a server, if it is currently running."""
    True


@click.command()
@click.argument('server')
async def killProcess(server: str):
    """Kills the process corresponding to the given servername."""
    True


@click.command()
@click.argument('server')
async def status(server: str):
    """Checks if a server's process is running."""
    True


@click.command()
@click.argument('server')
async def backup(*server: str):
    """Backs up all given servers."""
    True


@click.command()
@click.argument('server')
async def keepBack(*server: str):
    """Moves latest backup of given servers to configured location."""
    True


if __name__ == '__main__':
    # TODO: Standalone use with click and check for valid server target.
    # TODO: Implement Setuptools for this and charfred;
    True
