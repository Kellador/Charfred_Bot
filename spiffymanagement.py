import logging
import os
import re
import tarfile
from datetime import datetime
from pathlib import Path
from subprocess import run
from time import sleep, time
from typing import TYPE_CHECKING, List

import psutil

if TYPE_CHECKING:
    from spiffy import Settings

log = logging.getLogger('spiffymanagement')


def screenCmd(server, *cmds):
    for cmd in cmds:
        run(['screen', '-S', server, '-X', 'stuff', f'{cmd}\r'])


def run_startup_commands(server):
    """
    Custom commands ran at startup with a delay
    """
    if server in ('Techopolis',):  # Short startup times
        sleepy = (80, 10)
    elif server in ('Rag6',):  # Long startup times
        sleepy = (240, 10)
    else:  # Everything else
        sleepy = (180, 10)

    log.info('Forceload removing %s in T minus %d!', server, sleepy[0])
    sleep(sleepy[0])
    forceload_removeall(server)

    if server in ('Techopolis',):
        trigger_reload(server)

    sleep(sleepy[1])
    forceload_removeall(server)
    log.info('You\'re not you, you\'re me!')


def forceload_removeall(server):
    """
    Some servers do not unload chunks properly unless being forced
    """
    screenCmd(server, 'forceload remove all')
    screenCmd(
        server, 'execute in compactmachines:compact_world run forceload remove all'
    )


def trigger_reload(server):
    """
    Some servers do not come up correctly without forcing a config reload
    """
    log.info("Triggering /reload on %s", server)
    screenCmd(server, 'reload')


class LoggedException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def log_this(self):
        log.error(self.message)


class ServerNotFound(LoggedException):
    def __init__(self, sdir: Path) -> None:
        super().__init__(f'{sdir} does not exist')


class NoInvocation(LoggedException):
    def __init__(self, sdir: Path) -> None:
        super().__init__(f'{sdir} does not contain a \'spiffy_invocation\' file')


class ParentDirMissing(LoggedException):
    def __init__(self, path: Path) -> None:
        super().__init__(f'{path} does not exist!')


class NothingToBackup(LoggedException):
    def __init__(self, path: Path) -> None:
        super().__init__(
            f'{path} contains no \'world\' directory and has no '
            '\'spiffy_backup\' file specifying other directories to back up'
        )


def find_server(path: Path, name: str) -> Path:
    """Find a minecraft server.

    Parameters
    ----------
    path
        parent directory of minecraft server directories
    name
        name of server to find

    Returns
    -------
        path to server

    Raises
    ------
    ParentDirMissing
        raised if parent directory does not exist
    NoInvocation
        raised if server exists but has no 'spiffy_invocation'
    ServerNotFound
        raised if server cannot be found
    """

    if not path.exists():
        raise ParentDirMissing(path)

    sdir = path / name
    if sdir.exists():
        si = sdir / 'spiffy_invocation'
        if si.exists():
            return sdir
        else:
            raise NoInvocation(sdir)
    else:
        raise ServerNotFound(sdir)


def get_invocation(serverdir: Path) -> List[str]:
    """Get invocation from a given server.

    Parameters
    ----------
    serverdir
        path to server

    Returns
    -------
        contents of 'spiffy_invocation' file as a list
        of command components
    """

    si = serverdir / 'spiffy_invocation'

    with si.open() as file:
        invocation = file.read().split()

    return invocation


def get_backup(serverdir: Path) -> dict[str, List[Path]]:
    """Get all directories to backup for a given server.

    Parameters
    ----------
    serverdir
        directory of server to perform backup on

    Returns
    -------
        a dict of paths to include and exclude
    """

    world = serverdir / 'world'
    sb = serverdir / 'spiffy_backup'

    def _read_specification() -> dict[str, List[Path]]:
        with sb.open() as file:
            entries = file.read().split()

        specs = {'include': [], 'exclude': []}

        for e in entries:
            if e.startswith('-'):
                e_path = serverdir / e[1:]
                if e_path.exists():
                    specs['exclude'].append(e_path)
            else:
                if e.startswith('+'):  # Seems logical one might do this, so why not?!
                    e = e[1:]
                i_path = serverdir / e
                if i_path.exists():
                    specs['include'].append(i_path)

        return specs

    match world.exists(), sb.exists():
        case True, True:
            specification = _read_specification()
            if world not in specification['include']:
                specification['include'].append(world)
        case True, False:
            specification = {'include': [world], 'exclude': []}
        case False, True:
            specification = _read_specification()
        case False, False:
            raise NothingToBackup(serverdir)

    return specification


def isUp(server: str) -> bool:
    """Determine if a server is running.

    Parameters
    ----------
    server
        name of server, must be in the server's
        invocation in the form '<server>.jar' somewhere

    Returns
    -------
        boolean indicating running or not
    """

    for process in psutil.process_iter(attrs=['cmdline']):
        if f'{server}.jar' in process.info['cmdline']:
            return True
    return False


def termProc(server: str) -> bool:
    """Finds the process for a given server and terminates it.

    Parameters
    ----------
    server
        name of server, must be in server's invocation
        in the form of '<server>.jar' somewhere

    Returns
    -------
        True if process was found and successfully terminated
        False if process was not found
    """

    for process in psutil.process_iter(attrs=['cmdline']):
        if f'{server}.jar' in process.info['cmdline']:
            toKill = process.children()
            toKill.append(process)
            for p in toKill:
                p.terminate()
            _, alive = psutil.wait_procs(toKill, timeout=3)
            for p in alive:
                p.kill()
            _, alive = psutil.wait_procs(toKill, timeout=3)
            if not alive:
                return True

    return False


def buildCountdownSteps(cntd):
    """Builds and returns a list of countdown step triples,
    consisting of 'time to announce', 'time in seconds to wait',
    and 'the timeunit to announce'.
    """

    countpat = re.compile(
        '(?P<time>\d+)((?P<minutes>[m].*)|(?P<seconds>[s].*))', flags=re.I
    )
    steps = []
    for i, step in enumerate(cntd):
        s = countpat.search(step)
        if s.group('minutes'):
            time = int(s.group('time'))
            secs = time * 60
            unit = 'minutes'
        else:
            time = int(s.group('time'))
            secs = time
            unit = 'seconds'
        if i + 1 > len(cntd) - 1:
            steps.append((time, secs, unit))
        else:
            st = countpat.search(cntd[i + 1])
            if st.group('minutes'):
                t = int(st.group('time')) * 60
            else:
                t = int(st.group('time'))
            steps.append((time, secs - t, unit))
    return steps


def start(cfg: 'Settings', server: str):
    """Starts a server, if it is not running already."""

    try:
        server_path = find_server(cfg.parent_directory, server)
    except (ParentDirMissing, ServerNotFound, NoInvocation) as e:
        e.log_this()
        return

    if isUp(server):
        log.info(f'{server} appears to be running already!')
    else:
        invocation = get_invocation(server_path)
        os.chdir(server_path)
        log.info(f'Starting {server}')
        run(['screen', '-h', '5000', '-dmS', server, *invocation, 'nogui'])
        sleep(5)
        if isUp(server):
            log.info(f'{server} is now running!')
            # run_startup_commands(server)
        else:
            log.warning(f'{server} does not appear to have started!')


def stop(cfg: 'Settings', server, countdown=None):
    """Stops a server immediately, if it is currently running."""

    if isUp(server):
        if countdown:
            countdownSteps = [
                "20m",
                "15m",
                "10m",
                "5m",
                "3m",
                "2m",
                "1m",
                "30s",
                "10s",
                "5s",
            ]
            if countdown not in countdownSteps:
                log.error(f'{countdown} is an undefined step, aborting!')
                availableSteps1 = ', '.join(countdownSteps[:5])
                availableSteps2 = ', '.join(countdownSteps[5:])
                log.info(
                    '> Available countdown steps are:\n'
                    f'> {availableSteps1},\n'
                    f'> {availableSteps2}'
                )
                return
            log.info(f'Stopping {server} with {countdown}-countdown.')
            indx = countdownSteps.index(countdown)
            cntd = countdownSteps[indx:]
            steps = buildCountdownSteps(cntd)
            for step in steps:
                screenCmd(
                    server,
                    'title @a times 20 40 20',
                    f'title @a subtitle {{\"text\":\"in {step[0]} {step[2]}!\",\"italic\":true}}',
                    'title @a title {\"text\":\"Stopping\", \"bold\":true}',
                    f'tellraw @a {{\"text\":\"[Stopping in {step[0]} {step[2]}!]\",\"color\":\"green\"}}',
                )
                sleep(step[1])

        log.info(f'Stopping {server} now...')
        screenCmd(
            server,
            'title @a times 20 40 20',
            'title @a title {\"text\":\"STOPPING SERVER NOW\", \"bold\":true, \"italic\":true}',
            f'tellraw @a {{\"text\":\"[Stopping now!]\",\"color\":\"green\"}}'
            'save-all',
        )
        sleep(15)
        screenCmd(server, 'stop')
        waiting = 6
        while isUp(server) and waiting > 0:
            waiting -= 1
            sleep(20)
        if isUp(server):
            log.warning(f'{server} does not appear to have stopped!')

            log.warning(f'Terminating {server} process!')
            terminated = terminate(server)
            if not terminated:
                return

        log.info(f'{server} was stopped.')
    else:
        log.info(f'{server} already is not running.')


def restart(cfg: 'Settings', server, countdown=None):
    """Restarts a server with a countdown, if it is currently running."""

    try:
        server_path = find_server(cfg.parent_directory, server)
    except (ParentDirMissing, ServerNotFound, NoInvocation) as e:
        e.log_this()
        return

    if isUp(server):
        countdownSteps = [
            "20m",
            "15m",
            "10m",
            "5m",
            "3m",
            "2m",
            "1m",
            "30s",
            "10s",
            "5s",
        ]
        if countdown:
            if countdown not in countdownSteps:
                log.error(f'{countdown} is an undefined step, aborting!')
                availableSteps1 = ', '.join(countdownSteps[:5])
                availableSteps2 = ', '.join(countdownSteps[5:])
                log.info(
                    '> Available countdown steps are:\n'
                    f'> {availableSteps1},\n'
                    f'> {availableSteps2}'
                )
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
                f'tellraw @a {{\"text\":\"[Restarting in {step[0]} {step[2]}!]\",\"color\":\"green\"}}',
            )
            sleep(step[1])
        screenCmd(server, 'save-all')
        sleep(15)
        screenCmd(server, 'stop')
        waiting = 6
        while isUp(server) and waiting > 0:
            waiting -= 1
            sleep(20)
        if isUp(server):
            log.warning(f'Restart failed, {server} appears not to have stopped!')

            log.warning(f'Terminating {server} process!')
            terminated = terminate(server)
            if not terminated:
                return

        log.info('Restart in progress...')
        invocation = get_invocation(server_path)
        log.info(f'Starting {server}')
        os.chdir(server_path)
        run(['screen', '-h', '5000', '-dmS', server, *invocation, 'nogui'])
        sleep(5)
        if isUp(server):
            log.info(f'Restart successful, {server} is now running!')
            # run_startup_commands(server)
            return True
        else:
            log.warning(f'Restart failed, {server} does not appear to have started!')
            return False
    else:
        log.warning(f'Restart cancelled, {server} is offline!')
        return False


def terminate(server: str) -> bool:
    """Terminate a server process, forcefully.

    Parameters
    ----------
    server
        name of server, must be in server's invocation
        in the form of '<server>.jar' somewhere

    Returns
    -------
        a bool indicating successful termination
    """

    result = termProc(server)
    if result:
        log.info(f'{server} has been terminated!')
    else:
        log.warning(f'{server} termination failed! Oh dear...')
    return result


def status(server: str):
    """Checks if a server's process is running."""

    if isUp(server):
        log.info(f'{server} is running.')
    else:
        log.info(f'{server} is not running.')


def backup(cfg: 'Settings', server: str, specific_path: str | None = None):
    """Perform backup of a given server.

    Backups always include the 'world' directory if it exists,
    further directories may be specified in a 'spiffy_backup' file
    inside the server's directory;

    Alternatively specific backups may be performed by calling this
    function with the 'specific_path' parameter pointing to a
    given servers subdirectory or file to back up instead.
    """

    try:
        server_path = find_server(cfg.parent_directory, server)
    except (ParentDirMissing, ServerNotFound) as e:
        e.log_this()
        return
    except NoInvocation:
        pass

    if specific_path:
        _source = server_path / specific_path
        if _source.exists():
            specification = {
                'include': [_source],
                'exclude': [],
            }
        else:
            try:
                Path(specific_path).relative_to(server_path)
            except ValueError:
                log.error(f'{specific_path} is not a subpath of {server_path}!')
                return
            else:
                specification = {
                    'include': [specific_path],
                    'exclude': [],
                }
    else:
        try:
            specification = get_backup(server_path)
        except NothingToBackup as e:
            e.log_this()
            return
        else:
            if not specification['include']:
                log.warning(f'Back up job for {server} failed, nothing to back up!')
                return

    log.info(f'Starting backup for {server}...')
    if isUp(server):
        log.info(f'{server} is running, announcing backup and toggling save!')
        screenCmd(server, 'Starting Backup!', 'save-off', 'save-all')
        sleep(10)

    now = time()
    now_str = datetime.now().strftime('%Y.%m.%d_%H_%M_%S')

    backup_location = cfg.backup_directory / server
    backup_location.mkdir(parents=True, exist_ok=True)

    log.info('Cleaning up backups...')

    for d in backup_location.iterdir():
        if d.is_dir() and not d.name.startswith('.'):
            if d.stat().st_mtime < now - (cfg.backup_maxAge * 60):
                for e in d.iterdir():
                    if e.is_file():
                        e.unlink()
                        log.info(f'Deleted \'{e}\'')
                    if e.is_dir():
                        log.warning(f'Found directory {e.name} in {d} during cleanup!')
                        log.warning(
                            f'Please remove {e} manually if it is no longer needed!'
                        )
                try:
                    d.rmdir()
                except OSError:
                    log.warning(
                        f'Outdated backup directory {d} could not be fully removed!'
                    )
                    log.warning(
                        'This is likely because an unpacked backup still exists within.'
                    )
                else:
                    log.info(f'Cleaned up outdated backup directory \'{d}\'')

    log.info(f'Creating backup(s) specified for {server}...')

    target_path = backup_location / f'{now_str}'
    target_path.mkdir(exist_ok=True)

    os.chdir(target_path)

    for source_path in specification['include']:
        log.info(f'Backing up \'{source_path}\'...')
        try:
            filename = source_path.relative_to(server_path)
        except ValueError:
            log.critical(f'\'{source_path}\' is not a subpath of the specified server!')
            log.error(
                'This should not be possible. Backup aborted! Please contact someone!'
            )
            return
        else:
            filename = '.'.join(filename.parts)

        exclusions = [
            f'{p.relative_to(source_path)}'
            for p in specification['exclude']
            if p.is_relative_to(source_path)
        ]

        def _filter(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
            if any(tarinfo.name.startswith(ex) for ex in exclusions):
                return None
            else:
                return tarinfo

        with tarfile.open(f'{filename}.tar.gz', 'w:gz') as tf:
            if exclusions:
                tf.add(source_path, source_path.name, filter=_filter)
            else:
                tf.add(source_path, source_path.name)
        log.info(f'\'{source_path}\' backed up!')

    log.info(f'Backup(s) created for {server}!')

    if isUp(server):
        log.info(f'{server} is running, re-enabling save!')
        screenCmd(server, 'save-on', 'Backup complete!')
