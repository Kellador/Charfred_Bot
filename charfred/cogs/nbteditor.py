#!/usr/bin/env python

from discord.ext import commands
from ..utils.discoutils import has_perms, _is_cmdChannel


class nbteditor:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @_is_cmdChannel()
    @has_perms()
    async def nbt(self, ctx):
        True


def setup(bot):
    bot.add_cog(nbteditor(bot))
