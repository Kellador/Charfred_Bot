#!/usr/bin/env python

from discord.ext import commands
import sys
import traceback
import datetime
import random
import aiohttp
from keywords import nacks, errormsgs
from utils.miscutils import getPasteKey
import configs as cfg
from ttldict import TTLOrderedDict

description = """
Charfred is a gentleman and a scholar,
he will do whatever you ask of him to the best of his abilities,
however he can be quite rude sometimes.
"""

prime_cogs = ()


def prefix_callable(bot, msg):
    bot_id = bot.user.id
    prefixes = [f'<@{bot_id}> ', f'<@!{bot_id}>']
    prefixes.extend(cfg.prefixes)
    return prefixes


class Charfred(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix_callable, description=description,
                         pm_help=False)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.stalkdict = TTLOrderedDict(default_ttl=60)
        for cog in prime_cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                print(f'Failed to load cog {cog}!')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(random.choice(errormsgs))
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(random.choice(errormsgs))
            print(f'{ctx.author.name} attempted to use {ctx.command.name}!')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(random.choice(nacks))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send('Sorry lass, that command\'s on cooldown!')
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(random.choice(nacks))
            print(f'{ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(f'{error.original.__class__.__name__}: {error.original}',
                  file=sys.stderr)

    async def on_ready(self):
        print(f'{self.user} reporting for duty!\nID: {self.user.id}')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        if not hasattr(self, 'pasteKey'):
            self.pasteKey = await getPasteKey(self.session)
            print(f'Pastebin user key recieved: {self.pasteKey}')

    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            await self.process_commands(message)

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        if cfg.liveMode:
            token = cfg.liveBotToken
        else:
            token = cfg.stageBotToken
        super().run(token, reconnect=True)


char = Charfred()
char.run()
