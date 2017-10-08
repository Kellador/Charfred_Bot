#!/usr/bin/env python

import psutil
import asyncio
import logging as log
from .. import configs as cfg


async def getPasteKey(session):
    async with session as cs:
        async with cs.post(
            'https://pastebin.com/api/api_login.php',
            params={'api_dev_key': cfg.pastebinToken,
                    'api_user_name': cfg.pastebinUser,
                    'api_user_password': cfg.pastebinPass}) as resp:
            return await resp.text()


def isUp(server):
    """Checks whether a server is up, by searching for its process."""
    for process in psutil.process_iter(attrs=['cmdline']):
        if f'{server}.jar' in process.info['cmdline']:
            return True
    return False


async def sendCmd(server, cmd):
    """Passes a given command string to a server's screen."""
    log.info(f'Sending \"{cmd}\" to {server}.')
    await asyncio.create_subprocess_exec(
        'screen', '-S', server, '-X', 'stuff', f'{cmd}$(printf \\r)'
    )


async def sendCmds(server, *cmds):
    """Passes all given command strings to a server's screen."""
    for cmd in cmds:
        log.info(f'Sending \"{cmd}\" to {server}.')
        await asyncio.create_subprocess_exec(
            'screen', '-S', server, '-X', 'stuff', f'{cmd}$(printf \\r)'
        )
