#!/usr/bin/env python

from discord.ext import commands
from discord import ClientException
import os
import logging
import coloredlogs
import traceback
import datetime
import random
import aiohttp
from cogs.configs.keywords import nacks, errormsgs
from cogs.utils.miscutils import getPasteKey
from cogs.utils.config import Config
from cogs.configs import configs

log = logging.getLogger('charfred')
# coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

description = """
Charfred is a gentleman and a scholar,
he will do whatever you ask of him to the best of his abilities,
however he can be quite rude sometimes.
"""


def get_prefixes(bot, msg):
    prefixes = ['‽']
    prefixes.extend(configs.prefixes)
    return commands.when_mentioned_or(*prefixes)(bot, msg)


class Charfred(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefixes, description=description,
                         pm_help=False)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.servercfg = Config(f'{self.dir}/cogs/configs/serverCfgs.json',
                                default=f'{self.dir}/cogs/configs/serverCfgs.json_default',
                                load=True, loop=self.loop)
        try:
            self.load_extension('cogs.gearbox')
        except ClientException:
            log.critical(f'Could not load \"Gearbox\"!')
        except ImportError:
            log.critical(f'Gearbox could not be imported!')
            traceback.print_exc()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(random.choice(errormsgs))
            log.warning(f'DisabledCommand: {ctx.invoked_with}')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(random.choice(errormsgs))
            log.warning(f'{ctx.author.name} attempted to use {ctx.command.name} in {ctx.channel.name}!')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(random.choice(nacks))
            log.warning(f'CommandNotFound: {ctx.invoked_with}')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send('Sorry lass, that command\'s on cooldown!')
            log.warning(f'CommandOnCooldown: {ctx.invoked_with}')
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(random.choice(nacks))
            log.error(f'{ctx.command.qualified_name}:')
            traceback.print_tb(error.original.__traceback__)
            log.error(f'{error.original.__class__.__name__}: {error.original}')

    async def on_ready(self):
        log.info(f'{self.user} reporting for duty!')
        log.info(f'ID: {self.user.id}')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        if not hasattr(self, 'pasteKey'):
            self.pasteKey = await getPasteKey(self.session)
            log.info(f'Pastebin user key recieved: {self.pasteKey}')

    async def on_message(self, message):
        if message.author.bot:
            return
        elif message.guild.id is None:
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
