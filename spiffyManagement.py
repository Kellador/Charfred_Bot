from subprocess import run
import os
from time import sleep, time
from datetime import datetime
import tarfile
import logging
from cogs.minecraftCogs.utils.mcservutils import isUp, termProc, buildCountdownSteps


log = logging.getLogger('spiffyManagement')


def screenCmd(server, *cmds):
    for cmd in cmds:
        run(['screen', '-S', server, '-X', 'stuff', f'{cmd}\r'])


def start(cfg, server):
    """Starts a server, if it is not running already."""

    if server not in cfg['servers']:
        log.warning(f'{server} has been misspelled or not configured!')
        return False
    if isUp(server):
        log.info(f'{server} appears to be running already!')
    else:
        os.chdir(cfg['serverspath'] + f'/{server}')
        log.info(f'Starting {server}')
        run(['screen', '-h', '5000', '-dmS', server,
             *(cfg['servers'][server]['invocation']).split(), 'nogui'])
        sleep(5)
        if isUp(server):
            log.info(f'{server} is now running!')
            return True
        else:
            log.warning(f'{server} does not appear to have started!')
            return False


def stop(cfg, server):
    """Stops a server immediately, if it is currently running."""

    if server not in cfg['servers']:
        log.warning(f'{server} has been misspelled or not configured!')
        return False
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

    if server not in cfg['servers']:
        log.warning(f'{server} has been misspelled or not configured!')
        return False
    if isUp(server):
        countdownSteps = ["20m", "15m", "10m", "5m", "3m",
                          "2m", "1m", "30s", "10s", "5s"]
        if countdown:
            if countdown not in countdownSteps:
                log.error(f'{countdown} is an undefined step, aborting!')
                availableSteps1 = ', '.join(countdownSteps[:5])
                availableSteps2 = ', '.join(countdownSteps[5:])
                log.info('> Available countdown steps are:\n'
                         f'> {availableSteps1},\n'
                         f'> {availableSteps2}')
                return False
            log.info(f'Restarting {server} with {countdown}-countdown.')
            indx = countdownSteps.index(countdown)
            cntd = countdownSteps[indx:]
        else:
            log.info(f'Restarting {server} with default 10min countdown.')
            cntd = countdownSteps[2:]
        steps = buildCountdownSteps(cntd)
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
            log.info(f'Starting {server}')
            os.chdir(cfg['serverspath'] + f'/{server}')
            run(['screen', '-h', '5000', '-dmS', server,
                *(cfg['servers'][server]['invocation']).split(), 'nogui'])
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


def terminate(cfg, server):
    """Terminates the process corresponding to the given servername."""

    if server not in cfg['servers']:
        log.warning(f'{server} has been misspelled or not configured!')
        return
    return termProc(server)


def status(cfg, server):
    """Checks if a server's process is running."""

    if server not in cfg['servers']:
        log.warning(f'{server} has been misspelled or not configured!')
        return False
    if isUp(server):
        log.info(f'{server} is running.')
        return True
    else:
        log.info(f'{server} is not running.')
        return False


def backup(cfg, server):
    """Backup a server's world directory.

    Also deletes backups older than a configured age.
    """

    bpath = cfg['backupspath']
    if server not in cfg['servers']:
        log.warning(f'{server} has been misspelled or not configured!')
    elif 'worldname' not in cfg['servers'][server]:
        log.warning(f'{server} has no world directory specified!')
    else:
        world = cfg['servers'][server]['worldname']
        log.info(f'Starting backup for {server}...')
        if isUp(server):
            log.info(f'{server} is running, announcing backup and toggling save!')
            screenCmd(
                server,
                'Starting Backup!',
                'save-off',
                'save-all'
            )
            sleep(10)
        sbpath = f'{bpath}/{server}'
        try:
            os.makedirs(sbpath, exist_ok=True)
        except Exception as e:
            log.error(e + '\nBackups aborted!')
            return False
        else:
            log.info('Created missing directories! (if they were missing)')
        log.info('Deleting outdated backups...')
        now = time()
        with os.scandir(sbpath) as d:
            for entry in d:
                if not entry.name.startswith('.') and entry.is_file():
                    stats = entry.stat()
                    if stats.st_mtime < now - (int(cfg['oldTimer']) * 60):
                        try:
                            os.remove(entry.path)
                        except OSError as e:
                            log.error(e)
                        else:
                            log.info(f'Deleted {entry.path} for being too old!')
        log.info('Creating backup...')
        bname = datetime.now().strftime('%Y.%m.%d-%H-%M-%S') + f'-{server}-{world}.tar.gz'
        os.chdir(sbpath)
        serverpath = cfg['serverspath']
        with tarfile.open(bname, 'w:gz') as tf:
            tf.add(f'{serverpath}/{server}/{world}', f'{world}')
        log.info('Backup created!')
        if isUp(server):
            log.info(f'{server} is running, re-enabling save!')
            screenCmd(
                server,
                'save-on',
                'say Backup complete!'
            )


def questbackup(cfg, server):
    """Silly solution to a silly problem."""

    bpath = cfg['backupspath']
    if server not in cfg['servers']:
        log.warning(f'{server} has been misspelled or not configured!')
    elif 'worldname' not in cfg['servers'][server]:
        log.warning(f'{server} has no world directory specified!')
    else:
        world = cfg['servers'][server]['worldname']
        log.info(f'Starting backup for {server}\'s quests...')
        if isUp(server):
            log.info(f'{server} is running, don\'t care, just want QUESTS!')
        sbpath = f'{bpath}/{server}/quests'
        try:
            os.makedirs(sbpath, exist_ok=True)
        except Exception as e:
            log.error(e + '\nBackup aborted, DANGER! might loose quests!')
            return False
        else:
            log.info('Created missing directories! (if they were missing)')
        log.info('Deleting old quest backups...')
        now = time()
        with os.scandir(sbpath) as d:
            for entry in d:
                if not entry.name.startswith('.') and entry.is_file():
                    stats = entry.stat()
                    if stats.st_mtime < now - (int(cfg['oldTimer']) * 60):
                        try:
                            os.remove(entry.path)
                        except OSError as e:
                            log.error(e)
                        else:
                            log.info(f'Deleted {entry.path} for being too old!')
        log.info('Creating quest backup...')
        bname = datetime.now().strftime('%Y.%m.%d-%H-%M-%S') + f'-{server}-{world}-QUESTS.tar.gz'
        os.chdir(sbpath)
        serverpath = cfg['serverspath']
        with tarfile.open(bname, 'w:gz') as tf:
            tf.add(f'{serverpath}/{server}/{world}/betterquesting', 'betterquesting')
        log.info('Quest backup created!')
        if isUp(server):
            log.info(f'{server} is running, STILL DON\'T CARE!')
        log.info('DONE!')
