#!/usr/bin/env python

import asyncio
import os
import tarfile
import datetime
import logging as log
from ..utils.miscutils import isUp, sendCmd, sendCmds


async def start(cfg, server):
    """Starts a server, if it is not running already."""
    if isUp(server):
        log.info(f'{server} appears to be running already!')
    else:
        cwd = os.getcwd()
        os.chdir(cfg['serverspath'] + f'/{server}')
        log.info(f'Starting {server}')
        await asyncio.create_subprocess_exec(
            'screen', '-h', '5000', '-dmS', server,
            cfg['servers'][server]['invocation'], 'nogui'
        )
        os.chdir(cwd)
        if isUp(server):
            log.info(f'{server} is now running!')
            return True
        else:
            log.warning(f'{server} does not appear to have started!')
            return False


async def stop(server):
    """Stops a server immediately, if it is currently running."""
    if isUp(server):
        log.info(f'Stopping {server}...')
        await sendCmds(
            server,
            'title @a times 20 40 20',
            'title @a title {\"text\":\"STOPPING SERVER NOW\", \"bold\":true, \"italic\":true}',
            'broadcast Stopping now!',
            'save-all',
        )
        asyncio.sleep(5)
        await sendCmd(self.loop,
            server,
            'stop'
        )
        asyncio.sleep(20)
        if isUp(server):
            log.warning(f'{server} does not appear to have stopped!')
            return False
        else:
            log.info(f'{server} was stopped.')
            return True
    else:
        log.info(f'{server} already is not running.')
        return True


async def restart(cfg, server, countdown=None):
    """Restarts a server with a countdown, if it is currently running."""
    if isUp(server):
        if countdown is None:
            log.info(f'Restarting {server} with default countdown.')
            cntd = cfg['restartCountdowns']['default']
        else:
            if countdown not in cfg['restartCountdowns']:
                log.error(f'{countdown} is undefined under restartCountdowns!')
                return False
            log.info(f'Restarting {server} with {countdown}-countdown.')
            cntd = cfg['restartCountdowns'][countdown]
        for step in cntd:
            # TODO
            True
    else:
        log.warning(f'Restart cancelled, {server} is offline!')
        return False


async def killProcess(server):
    """Kills the process corresponding to the given servername."""
    True


async def status(server):
    """Checks if a server's process is running."""
    if isUp(server):
        log.info(f'{server} is running.')
        return True
    else:
        log.info(f'{server} is not running.')
        return False


async def cleanBackups(cfg):
    """Deletes all backups older than the configured age."""
    cwd = os.getcwd()
    for server in iter(cfg['servers']):
        # TODO
        True


async def backup(cfg, server):
    """Backs up all given servers."""
    # TODO: Try this out!
    cwd = os.getcwd()
    if cfg['servers'][server]['backup']:
        if not isUp(server):
            log.warning(f'Skipping backup of {server} because it is offline. '
                        'Maybe it is currently restarting?')
            return
        try:
            os.mkdir(cfg['backupspath'] + f'/{server}')
            log.info(f'Created directory for {server} backup.')
        except OSError:
            pass
        try:
            os.chdir(cfg['serverspath'] + f'/{server}')
        except OSError as e:
            log.error(f'Could not backup {server}:\n{e.message}')
            return
        bfilename = (
            cfg['serverspath'] + f'/{server}/' +
            datetime.datetime.now().strftime('%Y.%m.%d-%H:%M') +
            f'-{server}-' + cfg['servers'][server]['worldname']
        )
        with tarfile.open(bfilename, 'w:gz') as tars:
            tars.add(cfg['servers'][server]['worldname'])
    os.chdir(cwd)


async def keepBack(cfg, server):
    """Moves latest backup of given servers to configured location."""
    True
