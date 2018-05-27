from discord.ext import commands
from discord import ClientException
import os
import asyncio
import click
import logging
import coloredlogs
import traceback
import datetime
import random
import aiohttp
from configs.keywords import nacks, errormsgs
from utils.config import Config

log = logging.getLogger('charfred')
coloredlogs.install(level='DEBUG',
                    logger=log,
                    fmt='%(asctime)s:%(msecs)03d %(name)s[%(process)d]: %(levelname)s %(message)s')

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    log.info('uvloop imported, oh yeah! \*high five\*')

description = """
Charfred is a gentleman and a scholar,
he will do whatever you ask of him to the best of his abilities,
however he can be quite rude sometimes.
"""


def _adminCogs(direc):
    for dirpath, _, filenames in os.walk(direc):
        if '__' in dirpath:
            continue
        else:
            for filename in filenames:
                if filename.endswith('.py'):
                    yield os.path.join(dirpath, filename[:-3])


class Charfred(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefixes, description=description,
                         pm_help=False)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.cfg = Config(f'{self.dir}/configs/botCfg.json',
                          load=True, loop=self.loop)
        try:
            os.chdir(self.dir)
            for adminCog in _adminCogs('adminCogs'):
                self.load_extension(adminCog.replace('/', '.').replace('\\', '.'))
        except ClientException:
            log.critical(f'Could not load Administrative Cogs!')
        except ImportError:
            log.critical(f'Administrative Cogs could not be imported!')
            traceback.print_exc()

    def get_prefixes(self, bot, msg):
        prefixes = []
        prefixes.extend(self.cfg['prefixes'])
        return commands.when_mentioned_or(*prefixes)(bot, msg)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await ctx.send('Sorry chap, that command\'s disabled!')
            log.warning(f'DisabledCommand: {ctx.command.qualified_name}')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(random.choice(errormsgs))
            log.warning(f'CheckFailure: {ctx.author.name}: {ctx.command.qualified_name} in {ctx.channel.name}!')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(random.choice(nacks))
            log.warning(f'CommandNotFound: {ctx.invoked_with}')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You\'re missing some arguments there, mate!')
            log.warning(f'MissingRequiredArgument: {ctx.command.qualified_name}')
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send('Stop it, you\'re making me blush...')
            log.warning(f'NoPrivateMessage: {ctx.author.name}: {ctx.command.qualified_name}')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(random.choice(errormsgs))
            log.warning(f'MissingPermissions: {ctx.author.name}: {ctx.command.qualified_name}')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('I am not allowed to do that, sir, it is known!')
            log.warning(f'BotMissingPermissions: {ctx.command.qualified_name}')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send('Sorry lass, that command\'s on cooldown!\n'
                           f'Try again in {error.retry_after} seconds.')
            log.warning(f'CommandOnCooldown: {ctx.command.qualified_name}')
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

    async def on_message(self, message):
        if message.author.bot:
            return
        elif message.guild.id is None:
            return
        else:
            log.info(f'[{message.author.name}]: {message.content}')
            await self.process_commands(message)

    async def close(self):
        await super().close()
        await self.session.close()

    def run(self, token=None):
        if token is None:
            log.info('Using pre-configured Token...')
            token = self.cfg['botToken']
        super().run(token, reconnect=True)


@click.command()
@click.option('--token', default=None, help='Discord Bot Token')
def run(token):
    log.info('Initializing Charfred!')
    char = Charfred()
    char.run(token)


if __name__ == '__main__':
    run()
