import click
import os
from spiffyScripts import spiffyManagement
from utils.config import Config


pass_cfg = click.make_pass_decorator(Config, ensure=True)
dirp = os.path.dirname(os.path.realpath(__file__))


@click.group()
@pass_cfg
def spiffy(cfg):
    cfg.cfgfile = f'{dirp}/serverCfgs.json'
    cfg._load()


@spiffy.command()
@click.argument('server')
@pass_cfg
def start(cfg, server):
    spiffyManagement.start(cfg, server)


@spiffy.command()
@click.argument('server')
def stop(server):
    spiffyManagement.stop(server)


@spiffy.command()
@click.argument('server')
@click.argument('countdown')
@pass_cfg
def restart(cfg, server, countdown):
    spiffyManagement.restart(cfg, server, countdown)


@spiffy.command()
@click.argument('server')
def status(server):
    spiffyManagement.status(server)


@spiffy.command()
@click.argument('servers', nargs=-1)
@pass_cfg
def backup(cfg, servers):
    for server in servers:
        spiffyManagement.backup(cfg, server)


@spiffy.command()
@click.argument('servers', nargs=-1)
@pass_cfg
def keepBack(cfg, servers):
    for server in servers:
        spiffyManagement.keepBack(cfg, server)


@spiffy.command()
@pass_cfg
def cleanBackups(cfg):
    spiffyManagement.cleanBackups(cfg)
