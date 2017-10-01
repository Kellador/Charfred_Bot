#!/usr/bin/env python

from discord.ext import commands
from ..utils.discoutils import has_perms
from ..utils.executors import exec_cmd_reply
from .. import configs as cfg


class serverCmds:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_perms()
    async def start(self, ctx, server: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['start']['Script'],
            'start',
            server
        )

    @commands.command()
    @has_perms()
    async def stop(self, ctx, server: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['stop']['Script'],
            'stop',
            server
        )

    @commands.command()
    @has_perms()
    async def restart(self, ctx, server: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['restart']['Script'],
            'restart',
            server
        )

    @commands.command()
    @has_perms()
    async def failsafe(self, ctx, server: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['failsafe']['Script'],
            'failsafe',
            server
        )

    @commands.command()
    @has_perms()
    async def status(self, ctx, server: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['status']['Script'],
            'status',
            server
        )


def setup(bot):
    bot.add_cog(serverCmds(bot))
