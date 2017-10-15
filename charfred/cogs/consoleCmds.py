#!/usr/bin/env python

from discord.ext import commands
import logging as log
from .utils.discoutils import sendReply_codeblocked, valid_server, has_permission
from .utils.miscutils import isUp, sendCmd


class consoleCmds:
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.servercfg = bot.servercfg

    @commands.group(invoke_without_command=True)
    @has_permission('whitelist')
    async def whitelist(self, ctx, player: str):
        msg = ['Command Log', '==========']
        for server in self.servercfg['servers']:
            if isUp(server):
                log.info(f'Whitelisting {player} on {server}.')
                await sendCmd(self.loop, server, f'whitelist add {player}')
                msg.append(f'[Info] Whitelisted {player} on {server}.')
            else:
                log.warning(f'Could not whitelist {player} on {server}.')
                msg.append(f'[Error]: Unable to whitelist {player}, {server} is offline!')
        await sendReply_codeblocked(ctx, '\n'.join(msg))

    @whitelist.command()
    @has_permission('whitelist')
    async def add(self, ctx, player: str):
        msg = ['Command Log', '==========']
        for server in self.servercfg['servers']:
            if isUp(server):
                log.info(f'Whitelisting {player} on {server}.')
                await sendCmd(self.loop, server, f'whitelist add {player}')
                msg.append(f'[Info] Whitelisted {player} on {server}.')
            else:
                log.warning(f'Could not whitelist {player} on {server}.')
                msg.append(f'[Error]: Unable to whitelist {player}, {server} is offline!')
        await sendReply_codeblocked(ctx, '\n'.join(msg))

    @whitelist.command()
    @has_permission('unwhitelist')
    async def remove(self, ctx, player: str):
        msg = ['Command Log', '==========']
        for server in self.servercfg['servers']:
            if isUp(server):
                log.info(f'Unwhitelisting {player} on {server}.')
                await sendCmd(self.loop, server, f'whitelist remove {player}')
                msg.append(f'[Info] Unwhitelisting {player} on {server}.')
            else:
                log.warning(f'Could not unwhitelist {player} on {server}.')
                msg.append(f'[Error]: Unable to unwhitelist {player}, {server} is offline!')
        await sendReply_codeblocked(ctx, '\n'.join(msg))

    @whitelist.command()
    @has_permission('whitelistcheck')
    async def check(self, ctx, player: str):
        msg = ['Command Log', '==========']
        for server in self.servercfg['servers']:
            with open(
                self.servercfg['serverspath'] + f'/{server}/whitelist.json', 'r'
            ) as whitelist:
                if player in whitelist.read():
                    msg.append(f'[Info] {player} is whitelisted on {server}.')
                else:
                    msg.append(f'[Warning]: {player} is NOT whitelisted on {server}.')
        await sendReply_codeblocked(ctx, '\n'.join(msg))

    @commands.command()
    @has_permission('kick')
    @valid_server()
    async def kick(self, ctx, server: str, player: str):
        msg = ['Command Log', '==========']
        if isUp(server):
            log.info(f'Kicking {player} from {server}.')
            await sendCmd(self.loop, server, f'kick {player}')
            msg.append(f'[Info] Kicked {player} from {server}.')
        else:
            msg.append(f'[Error] {server} is not online!')
        await sendReply_codeblocked(ctx, '\n'.join(msg))

    @commands.command()
    @has_permission('ban')
    async def ban(self, ctx, player: str):
        msg = ['Command Log', '==========']
        for server in self.servercfg['servers']:
            if isUp(server):
                log.info(f'Banning {player} on {server}.')
                await sendCmd(self.loop, server, f'ban {player}')
                log.info(f'Unwhitelisting {player} on {server}.')
                await sendCmd(self.loop, server, f'whitelist remove {player}')
                msg.append(f'[Info] Banned {player} from {server}.')
            else:
                log.warning(f'Could not ban {player} from {server}.')
                msg.append(f'[Error]: Unable to ban {player}, {server} is offline!')
        await sendReply_codeblocked(ctx, '\n'.join(msg))

    @commands.command()
    @has_permission('promote')
    async def promote(self, ctx, player: str, rank: str):
        msg = ['Command Log', '==========']
        for server in self.servercfg['servers']:
            if isUp(server):
                log.info(f'Promoting {player} to {rank}.')
                await sendCmd(
                    self.loop,
                    server,
                    self.servercfg['servers'][server]['promotecmd'].format(
                        player=player, rank=rank
                    )
                )
                msg.append(f'[Info] Promoted {player} to {rank} on {server}.')
            else:
                log.warning(f'Could not promote {player} on {server}.')
                msg.append(f'[Error]: Unable to promote {player}, {server} is offline!')
        await sendReply_codeblocked(ctx, '\n'.join(msg))

    @commands.command()
    @has_permission('demote')
    async def demote(self, ctx, player: str, rank: str):
        msg = ['Command Log', '==========']
        for server in self.servercfg['servers']:
            if isUp(server):
                log.info(f'Demoting {player} to {rank}.')
                await sendCmd(
                    self.loop,
                    server,
                    self.servercfg['servers'][server]['demotecmd'].format(
                        player=player, rank=rank
                    )
                )
                msg.append(f'[Info] Demoted {player} to {rank} on {server}.')
            else:
                log.warning(f'Could not demote {player} on {server}.')
                msg.append(f'[Error]: Unable to demote {player}, {server} is offline!')
        await sendReply_codeblocked(ctx, '\n'.join(msg))

    @commands.command(aliases=['pass'])
    @has_permission('relay')
    @valid_server()
    async def relay(self, ctx, server: str, command: str):
        msg = ['Command Log', '==========']
        if isUp(server):
            log.info(f'Relaying \"{command}\" to {server}.')
            await sendCmd(self.loop, server, command)
            msg.append(f'[Info] Relayed \"{command}\" to {server}.')
        else:
            log.warning(f'Could not relay \"{command}\" to {server}.')
            msg.append(f'[Error] Unable to relay command, {server} is offline!')
        await sendReply_codeblocked(ctx, '\n'.join(msg))


def setup(bot):
    bot.add_cog(consoleCmds(bot))
