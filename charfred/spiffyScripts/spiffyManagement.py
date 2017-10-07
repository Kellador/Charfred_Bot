#!/usr/bin/env python

import asyncio
import os
import glob
import tarfile
import datetime
import logging as log
from spiffyUtils import isUp, sendCmd, sendCmds


async def start(cfg, server):
    """Starts a server, if it is not running already."""
    if isUp(server):
        log.info(f'{server} appears to be running already!')
    else:
        cwd = os.getcwd()
        os.chdir(f'{cfg.serverspath}/{server}')
        log.info(f'Starting {server}')
        await asyncio.create_subprocess_exec(
            'screen', '-h', '5000', '-dmS', server,
            cfg.servers[server]['Invocation'], 'nogui'
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
        await sendCmd(
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
            cntd = cfg.restartCountdowns['default']
        else:
            if countdown not in cfg.restartCountdowns:
                log.error(f'{countdown} is undefined under restartCountdowns!')
                return False
            log.info(f'Restarting {server} with {countdown}-countdown.')
            cntd = cfg.restartCountdowns[countdown]
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
    for server in iter(cfg.servers):
        # TODO
        True


async def backup(cfg, *servers):
    """Backs up all given servers."""
    # TODO: Try this out!
    cwd = os.getcwd()
    for server in servers:
        if server in iter(cfg.servers) and cfg.servers[server]['backup']:
            if not isUp(server):
                log.warning(f'Skipping backup of {server} because it is offline. '
                            'Maybe it is currently restarting?')
                continue
            try:
                os.mkdir(f'{cfg.backupspath}/{server}')
                log.info(f'Created directory for {server} backup.')
            except OSError:
                pass
            try:
                os.chdir(f'{cfg.serverspath}/{server}')
            except OSError as e:
                log.error(f'Could not backup {server}:\n{e.message}')
                continue
            bfilename = (
                f'{cfg.backupspath}/{server}/' +
                datetime.datetime.now().strftime('%Y.%m.%d-%H:%M') +
                f'-{server}-' + cfg.servers[server]['worldname']
            )
            with tarfile.open(bfilename, 'w:gz') as tars:
                tars.add(cfg.servers[server]['worldname'])
    else:
        os.chdir(cwd)


async def keepBack(cfg, *server):
    """Moves latest backup of given servers to configured location."""
    True


async def getReport(cfg, server, age=None):
    """Retrieves the last crashreport for the given server;
    Takes a relative age parameter, 0 for the newest report,
    1 for the one before, etc.
    """
    if age is None:
        reportFile = sorted(
            glob.iglob(f'{cfg.serverspath}/{server}/crash-reports/*'),
            key=os.path.getmtime,
            reverse=True
        )[0]
    else:
        reportFile = sorted(
            glob.iglob(f'{cfg.serverspath}/{server}/crash-reports/*'),
            key=os.path.getmtime,
            reverse=True
        )[age]
    # TODO: Work out a python solution for this.
    # proc = await asyncio.create_subprocess_exec(
    #     'awk',
    #     '/^Time: /{e=1}/^-- Head/{e=1}/^-- Block/{e=1}/^-- Affected/{e=1}/^-- System/{e=0}/^A detailed/{e=0}{if(e==1){print}}',
    #     reportFile
    #     stdout=asyncio.subprocess.PIPE,
    #     stderr=asyncio.subprocess.PIPE
    # )
    # log.info(f'Getting report for {server}.')
    # stdout, stderr = await proc.communicate()
    # if proc.returncode == 0:
    #     log.info(f'Report retrieved successfully.')
    # else:
    #     log.warning('Failed to retrieve report!')
    # return stdout.decode().strip()
