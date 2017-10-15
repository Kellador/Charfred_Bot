#!/usr/bin/env python

from discord.ext import commands
import asyncio
import os
import re
import logging as log
from .utils.discoutils import has_permission, _is_cmdChannel
from .utils.miscutils import isUp, termProc, sendCmd, sendCmds


class serverCmds:
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.servercfg = bot.servercfg
        self.countpat = re.compile(
            '(?P<time>\d+)((?P<minutes>[m].*)|(?P<seconds>[s].*))', flags=re.I
        )

    @commands.group()
    @_is_cmdChannel()
    async def server(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @server.command(aliases=['failsafe'])
    @has_permission('start')
    async def start(self, ctx, server: str):
        if isUp(server):
            log.info(f'{server} appears to be running already!')
            await ctx.send(f'{server} appears to be running already!')
        else:
            cwd = os.getcwd()
            log.info(f'Starting {server}')
            await ctx.send(f'Starting {server}.')
            os.chdir(self.servercfg['serverspath'] + f'/{server}')
            proc = await asyncio.create_subprocess_exec(
                'screen', '-h', '5000', '-dmS', server,
                self.servercfg['servers'][server]['invocation'], 'nogui',
                loop=self.loop
            )
            await proc.wait()
            os.chdir(cwd)
            await asyncio.sleep(5, loop=self.loop)
            if isUp(server):
                log.info(f'{server} is now running!')
                await ctx.send(f'{server} is now running!')
            else:
                log.warning(f'{server} does not appear to have started!')
                await ctx.send(f'{server} does not appear to have started!')

    @server.command()
    @has_permission('stop')
    async def stop(self, ctx, server: str):
        if isUp(server):
            log.info(f'Stopping {server}...')
            await ctx.send(f'Stopping {server}')
            await sendCmds(
                self.loop,
                server,
                'title @a times 20 40 20',
                'title @a title {\"text\":\"STOPPING SERVER NOW\", \"bold\":true, \"italic\":true}',
                'broadcast Stopping now!',
                'save-all',
            )
            await asyncio.sleep(5, loop=self.loop)
            await sendCmd(
                self.loop,
                server,
                'stop'
            )
            await asyncio.sleep(20, loop=self.loop)
            if isUp(server):
                log.warning(f'{server} does not appear to have stopped!')
                await ctx.send(f'{server} does not appear to have stopped!')
            else:
                log.info(f'{server} was stopped.')
                await ctx.send(f'{server} was stopped.')
        else:
            log.info(f'{server} already is not running.')
            await ctx.send(f'{server} already is not running.')

    @server.command()
    @has_permission('restart')
    async def restart(self, ctx, server: str, countdown: str=None):
        if isUp(server):
            if countdown:
                if countdown not in self.servercfg['restartCountdowns']:
                    log.error(f'{countdown} is undefined under restartCountdowns!')
                    await ctx.send(f'{countdown} is undefined under restartCountdowns!')
                    return
                log.info(f'Restarting {server} with {countdown}-countdown.')
                await ctx.send(f'Restarting {server} with {countdown}-countdown.')
                cntd = self.servercfg['restartCountdowns'][countdown]
            else:
                log.info(f'Restarting {server} with default countdown.')
                await ctx.send(f'Restarting {server} with default countdown.')
                cntd = self.servercfg['restartCountdowns']['default']
            steps = []
            for i, step in enumerate(cntd):
                s = self.countpat(step)
                if s.group('minutes'):
                    time = int(s.group('time')) * 60
                    unit = 'minutes'
                else:
                    time = int(s.group('time'))
                    unit = 'seconds'
                if i + 1 > len(cntd) - 1:
                    steps.append((time, time, unit))
                else:
                    st = self.countpat(cntd[i + 1])
                    if st.group('minutes'):
                        t = int(st.group('time')) * 60
                    else:
                        t = int(st.group('time'))
                    steps.append((time, time - t, unit))
            for step in steps:
                await sendCmds(
                    self.loop,
                    server,
                    'title @a times 20 40 20',
                    f'title @a subtitle {{\"text\":\"in {step[0]} {step[2]}!\",\"italic\":true}}',
                    'title @a title {\"text\":\"Restarting\", \"bold\":true}',
                    f'broadcast Restarting in {step[0]} {step[2]}!'
                )
                await ctx.send(f'Restarting {server} in {step[0]} {step[2]}')
                await asyncio.sleep(step[1], loop=self.loop)
            await sendCmd(
                self.loop,
                server,
                'save-all'
            )
            await asyncio.sleep(5, loop=self.loop)
            await sendCmd(
                self.loop,
                server,
                'stop'
            )
            await ctx.send(f'Stopping {server}.')
            await asyncio.sleep(30, loop=self.loop)
            if isUp(server):
                log.warning(f'Restart failed, {server} appears not to have stopped!')
                await ctx.send(f'Restart failed, {server} appears not to have stooped!')
            else:
                log.info(f'Restart in progress, {server} was stopped.')
                await ctx.send(f'Restart in progress, {server} was stopped.')
                cwd = os.getcwd()
                log.info(f'Starting {server}')
                await ctx.send(f'Starting {server}.')
                os.chdir(self.servercfg['serverspath'] + f'/{server}')
                proc = await asyncio.create_subprocess_exec(
                    'screen', '-h', '5000', '-dmS', server,
                    self.servercfg['servers'][server]['invocation'], 'nogui',
                    loop=self.loop
                )
                await proc.wait()
                os.chdir(cwd)
                await asyncio.sleep(5, loop=self.loop)
                if isUp(server):
                    log.info(f'Restart successful, {server} is now running!')
                    await ctx.send(f'Restart successful, {server} is now running!')
                else:
                    log.warning(f'Restart failed, {server} does not appear to have started!')
                    await ctx.send(f'Restart failed, {server} does not appear to have started!')
        else:
            log.warning(f'Restart cancelled, {server} is offline!')
            await ctx.send(f'Restart cancelled, {server} is offline!')

    @server.command()
    @has_permission('status')
    async def status(self, ctx, server: str):
        if isUp(server):
            log.info(f'{server} is running.')
            await ctx.send(f'{server} is running.')
        else:
            log.info(f'{server} is not running.')
            await ctx.send(f'{server} is not running.')

    @server.command()
    @has_permission('terminate')
    async def terminate(self, ctx, server: str):
        if termProc(server):
            log.info(f'Terminating {server}.')
            await ctx.send(f'Terminating {server}.')
        else:
            log.info(f'Could not terminate, {server} process not found.')
            await ctx.send(f'Could not terminate, {server} process not found.')


def setup(bot):
    bot.add_cog(serverCmds(bot))
