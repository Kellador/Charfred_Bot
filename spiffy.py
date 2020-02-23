import click
import os
import logging
import coloredlogs
import spiffymanagement
from utils.config import Config

log = logging.getLogger('spiffymanagement')
coloredlogs.install(level='DEBUG',
                    logger=log,
                    fmt='%(asctime)s:%(msecs)03d %(name)s: %(levelname)s %(message)s')

dirp = os.path.dirname(os.path.realpath(__file__))
cfg = Config(f'{dirp}/configs/serverCfgs.toml')


@click.group()
def spiffy():
    cfg._load()


@spiffy.command()
@click.argument('server')
def start(server):
    spiffymanagement.start(cfg, server)


@spiffy.command()
@click.argument('server')
def stop(server):
    spiffymanagement.stop(cfg, server)


@spiffy.command()
@click.argument('server')
@click.argument('countdown')
def restart(server, countdown):
    spiffymanagement.restart(cfg, server, countdown)


@spiffy.command()
@click.argument('server')
def status(server):
    spiffymanagement.status(cfg, server)


@spiffy.command()
@click.argument('servers', nargs=-1)
def backup(servers):
    for server in servers:
        spiffymanagement.backup(cfg, server)


@spiffy.command()
@click.argument('servers', nargs=-1)
def terminate(servers):
    for server in servers:
        spiffymanagement.terminate(cfg, server)


@spiffy.command()
@click.argument('servers', nargs=-1)
def questbackup(servers):
    for server in servers:
        spiffymanagement.questbackup(cfg, server)
