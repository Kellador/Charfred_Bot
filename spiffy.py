import click
import os
import spiffyManagement
from utils.config import Config


pass_cfg = click.make_pass_decorator(Config, ensure=True)
dirp = os.path.dirname(os.path.realpath(__file__))


@click.group()
@pass_cfg
def spiffy(cfg):
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
