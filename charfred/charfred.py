#!/usr/bin/env python

from discord.ext import commands
import os
import logging
import coloredlogs
import traceback
import datetime
import random
import aiohttp
from .keywords import nacks, errormsgs
from .utils.miscutils import getPasteKey
from .utils.config import Config
import configs
from ttldict import TTLOrderedDict

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)

description = """
Charfred is a gentleman and a scholar,
he will do whatever you ask of him to the best of his abilities,
however he can be quite rude sometimes.
"""

prime_cogs = ()


def prefix_callable(bot, msg):
    bot_id = bot.user.id
    prefixes = [f'<@{bot_id}> ', f'<@!{bot_id}>']
    prefixes.extend(configs.prefixes)
    return prefixes


class Charfred(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=prefix_callable, description=description,
                         pm_help=False)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.stalkdict = TTLOrderedDict(default_ttl=60)
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.servercfg = Config(f'{self.dir}/serverCfgs.json',
                                load=True, loop=self.loop)
        for cog in prime_cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                log.error(f'Failed to load cog {cog}!')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(random.choice(errormsgs))
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(random.choice(errormsgs))
            log.warning(f'{ctx.author.name} attempted to use {ctx.command.name} in {ctx.channel.name}!')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(random.choice(nacks))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send('Sorry lass, that command\'s on cooldown!')
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(random.choice(nacks))
            log.error(f'{ctx.command.qualified_name}:')
            traceback.print_tb(error.original.__traceback__)
            log.error(f'{error.original.__class__.__name__}: {error.original}')

    async def on_ready(self):
        print(f'{self.user} reporting for duty!\nID: {self.user.id}')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        if not hasattr(self, 'pasteKey'):
            self.pasteKey = await getPasteKey(self.session)
            log.info(f'Pastebin user key recieved: {self.pasteKey}')

    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            await self.process_commands(message)

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        if configs.liveMode:
            token = configs.liveBotToken
        else:
            token = configs.stageBotToken
        super().run(token, reconnect=True)


char = Charfred()
char.run()
