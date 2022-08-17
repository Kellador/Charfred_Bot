from pathlib import Path
import click
import os
import logging
import coloredlogs
import spiffymanagement
from utils import Store

log = logging.getLogger('spiffymanagement')
coloredlogs.install(level='DEBUG',
                    logger=log,
                    fmt='%(asctime)s:%(msecs)03d %(name)s: %(levelname)s %(message)s')

dirp = os.path.dirname(os.path.realpath(__file__))
_cfg = Store(Path(f'{dirp}/configs/botCfg'))
_cfg._load()


class Settings():
    def __init__(
        self,
        parent_directory: str,
        backup_directory: str,
        backup_maxAge: int
    ) -> None:
        self.parent_directory = Path(parent_directory)
        self.backup_directory = Path(backup_directory)
        self.backup_maxAge = backup_maxAge

cfg = Settings(
    parent_directory=_cfg['spiffy.parentdirectory'],
    backup_directory=_cfg['spiffy.backupdirectory'],
    backup_maxAge=int(_cfg['spiffy.backupmaxage'])
)


@click.group()
def spiffy():
    pass


@spiffy.command()
@click.argument('server')
def start(server):
    spiffymanagement.start(cfg, server)


@spiffy.command()
@click.argument('server')
@click.option('-c', '--countdown')
def stop(server, countdown):
    spiffymanagement.stop(cfg, server, countdown)


@spiffy.command()
@click.argument('server')
@click.argument('countdown')
def restart(server, countdown):
    spiffymanagement.restart(cfg, server, countdown)


@spiffy.command()
@click.argument('server')
def status(server):
    spiffymanagement.status(server)


@spiffy.command()
@click.argument('servers', nargs=-1)
def backup(servers):
    for server in servers:
        spiffymanagement.backup(cfg, server)


@spiffy.command()
@click.argument('servers', nargs=-1)
def terminate(servers):
    for server in servers:
        spiffymanagement.terminate(server)


@spiffy.command()
@click.argument('server')
@click.argument('specific_path')
def specialbackup(server, specific_path):
    spiffymanagement.backup(cfg, server, specific_path)
