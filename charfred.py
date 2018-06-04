from discord.ext import commands
from discord import ClientException
import os
import asyncio
import click
import logging
import coloredlogs
import traceback
import datetime
import aiohttp
from utils.config import Config

log = logging.getLogger('charfred')


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
        self.keywords = Config(f'{self.dir}/configs/keywords.json',
                               load=True, loop=self.loop,
                               default=f'{self.dir}/configs/keywords.json_default')
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

    async def on_command(self, ctx):
        log.info(f'[{ctx.author.name}]: {ctx.message.content}')

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
@click.option('--logLvl', default='DEBUG', help='Logging Level')
@click.option('--token', default=None, help='Discord Bot Token')
def run(logLvl, token):
    coloredlogs.install(level=logLvl,
                        logger=log,
                        fmt='%(asctime)s:%(msecs)03d %(name)s[%(process)d]: %(levelname)s %(message)s')
    log.info('Initializing Charfred!')
    char = Charfred()
    char.run(token)


if __name__ == '__main__':
    run()
