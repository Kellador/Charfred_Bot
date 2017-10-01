#!/usr/bin/env python

from discord.ext import commands
from ..utils.discoutils import has_perms
from ..utils.executors import exec_cmd_reply
from .. import configs as cfg


class playerCmds:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @has_perms()
    async def whitelist(self, ctx, player: str):
        if ctx.invoked_subcommand is None:
            await exec_cmd_reply(
                ctx,
                cfg.commands['add']['Script'],
                'whitelist',
                player
            )

    @whitelist.command()
    @has_perms()
    async def add(self, ctx, player: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['add']['Script'],
            'whitelist',
            player
        )

    @whitelist.command()
    @has_perms()
    async def remove(self, ctx, player: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['remove']['Script'],
            'unwhitelist',
            player
        )

    @whitelist.command()
    @has_perms()
    async def check(self, ctx, player: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['check']['Script'],
            'whitelistCheck',
            player
        )

    @commands.command()
    @has_perms()
    async def ban(self, ctx, player: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['crashreport']['Script'],
            player
        )

    @commands.command()
    @has_perms()
    async def promote(self, ctx, player: str, rank: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['crashreport']['Script'],
            player, rank
        )

    @commands.command()
    @has_perms()
    async def demote(self, ctx, player: str, rank: str):
        await exec_cmd_reply(
            ctx,
            cfg.commands['crashreport']['Script'],
            player, rank
        )


def setup(bot):
    bot.add_cog(playerCmds(bot))
