#!/usr/bin/env python

from discord.ext import commands
from ..utils.discoutils import has_perms, sendReply, sendReply_codeblocked


class playerCmds:
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @has_perms()
    async def whitelist(self, ctx):
        if ctx.invoked_subcommand is None:
            # TODO
            True

    @whitelist.command()
    async def add(self, ctx):
        # TODO
        True

    @whitelist.command()
    @has_perms()
    async def remove(self, ctx):
        # TODO
        True

    @whitelist.command()
    async def check(self, ctx):
        # TODO
        True

    @commands.command()
    @has_perms()
    async def ban(self, ctx):
        # TODO
        True

    @commands.command()
    @has_perms()
    async def promote(self, ctx):
        # TODO
        True

    @commands.command()
    @has_perms()
    async def demote(self, ctx):
        # TODO
        True


def setup(bot):
    bot.add_cog(playerCmds(bot))
