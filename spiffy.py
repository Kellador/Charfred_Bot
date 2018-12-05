import click
import os
import logging
import coloredlogs
import spiffyManagement
from utils.config import Config

log = logging.getLogger('spiffyManagement')


pass_cfg = click.make_pass_decorator(Config, ensure=True)
dirp = os.path.dirname(os.path.realpath(__file__))


@click.group()
@pass_cfg
def spiffy(cfg):
    coloredlogs.install(level='DEBUG',
                        logger=log,
                        fmt='%(asctime)s:%(msecs)03d %(name)s: %(levelname)s %(message)s')
    cfg.cfgfile = f'{dirp}/configs/serverCfgs.json'
    cfg._load()


@spiffy.command()
@click.argument('server')
@pass_cfg
def start(cfg, server):
    spiffyManagement.start(cfg, server)


@spiffy.command()
@click.argument('server')
@pass_cfg
def stop(cfg, server):
    spiffyManagement.stop(server)


@spiffy.command()
@click.argument('server')
@click.argument('countdown')
@pass_cfg
def restart(cfg, server, countdown):
    spiffyManagement.restart(cfg, server, countdown)


@spiffy.command()
@click.argument('server')
@pass_cfg
def status(cfg, server):
    spiffyManagement.status(server)


@spiffy.command()
@click.argument('servers', nargs=-1)
@pass_cfg
def backup(cfg, servers):
    for server in servers:
        spiffyManagement.backup(server)
