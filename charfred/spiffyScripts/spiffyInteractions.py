#!/usr/bin/env python

import logging as log
from spiffyUtils import isUp, sendCmd, sendCmds


async def whitelist(cfg, player):
    """Whitelists a player."""
    for server in iter(cfg['servers']):
        if isUp(server):
            log.info(f'Whitelisting {player} on {server}.')
            await sendCmd(server, f'whitelist add {player}')
        else:
            log.warning(f'Could not whitelist {player} on {server}.')


async def unwhitelist(cfg, player):
    """Removes a player from whitelist."""
    for server in iter(cfg['servers']):
        if isUp(server):
            log.info(f'Unwhitelisting {player} on {server}.')
            await sendCmd(server, f'whitelist remove {player}')
        else:
            log.warning(f'Could not unwhitelist {player} on {server}.')


async def checkwhitelist(cfg, player):
    """Checks whether a player is whitelisted or not."""
    True


async def kick(player, server):
    """Kicks a player from a given server."""
    if isUp(server):
        log.info(f'Kicking {player} from {server}.')
        await sendCmd(server, f'kick {player}')


async def ban(cfg, player):
    """Bans a player and removes him/her from the whitelist."""
    for server in iter(cfg['servers']):
        if isUp(server):
            log.info(f'Banning {player} on {server}.')
            await sendCmd(server, f'ban {player}')
            log.info(f'Unwhitelisting {player} on {server}.')
            await sendCmd(server, f'whitelist remove {player}')
        else:
            log.warning(f'Could not ban {player} from {server}.')


async def promote(cfg, player, rank):
    """Promotes a player to the given rank."""
    for server in iter(cfg['servers']):
        if isUp(server):
            log.info(f'Promoting {player} to {rank}.')
            await sendCmds(
                server,
                'lp user {player} parent add {rank}',
                'pex user {player} group set {rank}'
            )
        else:
            log.warning(f'Could not promote {player} on {server}.')


async def demote(cfg, player, rank):
    """Demotes a player to the given rank."""
    # TODO: This isn't quite right, implement rank commands from cfg.
    for server in iter(cfg['servers']):
        if isUp(server):
            log.info(f'Demoting {player} to {rank}.')
            await sendCmds(
                server,
                'lp user {player} parent set {rank}',
                'pex user {player} group set {rank}'
            )
        else:
            log.warning(f'Could not demote {player} on {server}.')


async def relay(server, command):
    """Relays a command to the given server's screen."""
    if isUp(server):
        log.info(f'Relaying \"{command}\" to {server}.')
        await sendCmd(server, command)
    else:
        log.warning(f'Could not relay \"{command}\" to {server}.')
