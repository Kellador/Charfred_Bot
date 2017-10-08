import click
import os
import asyncio
from functools import update_wrapper
import spiffyScripts.spiffyManagement as spiffyManagement
from ..utils.config import Config


pass_cfg = click.make_pass_decorator(Config, ensure=True)
dirp = os.path.dirname(os.path.realpath(__file__))


# NOTE: This is a rather ugly workaround to be able to use spiffyManagement
# without having to implement all its functions with and without async.
# TODO: Implement spiffyManagement without async for use here.
def cor(func):
    func = asyncio.coroutine(func)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    return update_wrapper(wrapper, func)


@click.group()
@pass_cfg
def spiffy(cfg):
    cfg.cfgfile = f'{dirp}/spiffyServers.json'
    cfg._load()


@spiffy.command()
@click.argument('server')
@pass_cfg
@cor
def start(cfg, server):
    yield from spiffyManagement.start(cfg, server)


@spiffy.command()
@click.argument('server')
@cor
def stop(server):
    yield from spiffyManagement.stop(server)


@spiffy.command()
@click.argument('server')
@click.argument('countdown')
@pass_cfg
@cor
def restart(cfg, server, countdown):
    yield from spiffyManagement.restart(cfg, server, countdown)


@spiffy.command()
@click.argument('server')
@cor
def status(server):
    yield from spiffyManagement.status(server)


@spiffy.command()
@click.argument('servers', nargs=-1)
@pass_cfg
@cor
def backup(cfg, servers):
    for server in servers:
        yield from spiffyManagement.backup(cfg, server)


@spiffy.command()
@click.argument('servers', nargs=-1)
@pass_cfg
@cor
def keepBack(cfg, servers):
    for server in servers:
        yield from spiffyManagement.keepBack(cfg, server)


@spiffy.command()
@pass_cfg
@cor
def cleanBackups(cfg):
    yield from spiffyManagement.cleanBackups(cfg)


if __name__ == '__main__':
    spiffy()
