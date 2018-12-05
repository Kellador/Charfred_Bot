import click
import os
import logging
import coloredlogs
import spiffyManagement
from utils.config import Config

log = logging.getLogger('spiffyManagement')
coloredlogs.install(level='DEBUG',
                    logger=log,
                    fmt='%(asctime)s:%(msecs)03d %(name)s: %(levelname)s %(message)s')

dirp = os.path.dirname(os.path.realpath(__file__))
cfg = Config(f'{dirp}/configs/serverCfgs.json')


@click.group()
def spiffy():
    cfg._load()


@spiffy.command()
@click.argument('server')
def start(server):
    spiffyManagement.start(cfg, server)


@spiffy.command()
@click.argument('server')
def stop(server):
    spiffyManagement.stop(cfg, server)


@spiffy.command()
@click.argument('server')
@click.argument('countdown')
def restart(server, countdown):
    spiffyManagement.restart(cfg, server, countdown)


@spiffy.command()
@click.argument('server')
def status(server):
    spiffyManagement.status(cfg, server)


@spiffy.command()
@click.argument('servers', nargs=-1)
def backup(servers):
    for server in servers:
        spiffyManagement.backup(server)
