#!/usr/bin/env python

from subprocess import run
import os
import tarfile
import datetime
import re
from time import sleep
import logging as log
from ..utils.miscutils import isUp, termProc


def screenCmd(server, *cmds):
    for cmd in cmds:
        run(['screen', '-S', server, '-X', 'stuff', f'{cmd}$(printf \\r)'])


def start(cfg, server):
    """Starts a server, if it is not running already."""
    if isUp(server):
        log.info(f'{server} appears to be running already!')
    else:
        cwd = os.getcwd()
        os.chdir(cfg['serverspath'] + f'/{server}')
        log.info(f'Starting {server}')
        run(['screen', '-h', '5000', '-dmS', server,
             cfg['servers'][server]['invocation'], 'nogui'])
        os.chdir(cwd)
        if isUp(server):
            log.info(f'{server} is now running!')
            return True
        else:
            log.warning(f'{server} does not appear to have started!')
            return False


def stop(server):
    """Stops a server immediately, if it is currently running."""
    if isUp(server):
        log.info(f'Stopping {server}...')
        screenCmd(
            server,
            'title @a times 20 40 20',
            'title @a title {\"text\":\"STOPPING SERVER NOW\", \"bold\":true, \"italic\":true}',
            'broadcast Stopping now!',
            'save-all',
        )
        sleep(5)
        screenCmd(
            server,
            'stop'
        )
        sleep(20)
        if isUp(server):
            log.warning(f'{server} does not appear to have stopped!')
            return False
        else:
            log.info(f'{server} was stopped.')
            return True
    else:
        log.info(f'{server} already is not running.')
        return True


def restart(cfg, server, countdown=None):
    """Restarts a server with a countdown, if it is currently running."""
    countpat = re.compile(
        '(?P<time>\d+)((?P<minutes>[m].*)|(?P<seconds>[s].*))', flags=re.I
    )
    if isUp(server):
        if countdown:
            if countdown not in cfg['restartCountdowns']:
                log.error(f'{countdown} is undefined under restartCountdowns!')
                return False
            log.info(f'Restarting {server} with {countdown}-countdown.')
            cntd = cfg['restartCountdowns'][countdown]
        else:
            log.info(f'Restarting {server} with default countdown.')
            cntd = cfg['restartCountdowns']['default']
        steps = []
        for i, step in enumerate(cntd):
            s = countpat(step)
            if s.group('minutes'):
                time = int(s.group('time')) * 60
                unit = 'minutes'
            else:
                time = int(s.group('time'))
                unit = 'seconds'
            if i + 1 > len(cntd) - 1:
                steps.append((time, time, unit))
            else:
                st = countpat(cntd[i + 1])
                if st.group('minutes'):
                    t = int(st.group('time')) * 60
                else:
                    t = int(st.group('time'))
                steps.append((time, time - t, unit))
        for step in steps:
            screenCmd(
                server,
                'title @a times 20 40 20',
                f'title @a subtitle {{\"text\":\"in {step[0]} {step[2]}!\",\"italic\":true}}',
                'title @a title {\"text\":\"Restarting\", \"bold\":true}',
                f'broadcast Restarting in {step[0]} {step[2]}!'
            )
            sleep(step[1])
        screenCmd(
            server,
            'save-all'
        )
        sleep(5)
        screenCmd(
            server,
            'stop'
        )
        sleep(30)
        if isUp(server):
            log.warning(f'Restart failed, {server} appears not to have stopped!')
        else:
            log.info(f'Restart in progress, {server} was stopped.')
            cwd = os.getcwd()
            log.info(f'Starting {server}')
            os.chdir(cfg['serverspath'] + f'/{server}')
            screenCmd(['screen', '-h', '5000', '-dmS', server,
                       cfg['servers'][server]['invocation'], 'nogui'])
            os.chdir(cwd)
            sleep(5)
            if isUp(server):
                log.info(f'Restart successful, {server} is now running!')
                return True
            else:
                log.warning(f'Restart failed, {server} does not appear to have started!')
                return False
    else:
        log.warning(f'Restart cancelled, {server} is offline!')
        return False


def terminate(server):
    """Terminates the process corresponding to the given servername."""
    return termProc(server)


def status(server):
    """Checks if a server's process is running."""
    if isUp(server):
        log.info(f'{server} is running.')
        return True
    else:
        log.info(f'{server} is not running.')
        return False


def cleanBackups(cfg):
    """Deletes all backups older than the configured age."""
    cwd = os.getcwd()
    for server in iter(cfg['servers']):
        # TODO
        pass


def backup(cfg, server):
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


def keepBack(cfg, server):
    """Moves latest backup of given servers to configured location."""
    # TODO
    pass
