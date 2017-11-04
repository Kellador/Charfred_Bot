import logging
import discord
from discord.ext import commands

log = logging.getLogger('charfred')


class moderation:
    def __init__(self, bot):
        self.bot = bot
        self.dir = bot.dir
        self.loop = bot.loop

    async def on_message(self, message):
        if message.author.id in (self.bot.user.id, self.bot.owner_id):
            return
        if message.guild.id is None:
            return

        if message.author.status is discord.Status.offline:
            await message.author.send(f'Don\'t be rude! Go online before you post!')