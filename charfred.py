import asyncio
import click
import logging
import coloredlogs
import traceback
import datetime
import aiohttp
import os
from pathlib import Path
from discord.ext import commands
from discord import ClientException, Intents
from utils import Config, CharfredContext

log = logging.getLogger('charfred')


try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    log.info('uvloop imported, oh yeah! *high five*')

description = """
Charfred is a gentleman and a scholar,
he will do whatever you ask of him to the best of his abilities,
however he can be quite rude sometimes.
"""


def _admincogs(direc):
    for dirpath, _, filenames in os.walk(direc):
        if '__' in dirpath:
            continue
        else:
            for filename in filenames:
                if filename.endswith('.py'):
                    yield os.path.join(dirpath, filename[:-3])


def _get_prefixes(bot, msg):
    bot_id = bot.user.id
    prefixes = [f'<@{bot_id}> ', f'<@!{bot_id}> ']
    if msg.guild:
        try:
            prefixes.extend(bot.cfg['prefix'][str(msg.guild.id)])
        except KeyError:
            pass
    return prefixes


class Charfred(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_get_prefixes, description=description,
                         pm_help=False, intents=Intents.all())
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.dir = Path(__file__).parent
        self.cfg = Config(f'{self.dir}/configs/botCfg.toml',
                          load=True, loop=self.loop)
        if 'prefix' not in self.cfg:
            self.cfg['prefix'] = {}
        if 'nodes' not in self.cfg:
            self.cfg['nodes'] = {}
        if 'hierarchy' not in self.cfg:
            self.cfg['hierarchy'] = []
        if 'cogcfgs' not in self.cfg:
            self.cfg['cogcfgs'] = {}
        self.cfg._save()

        self.keywords = Config(f'{self.dir}/configs/keywords.json',
                               load=True, loop=self.loop,
                               default=f'{self.dir}/configs/keywords.json_default')

        try:
            os.chdir(self.dir)
            for admincog in _admincogs('admincogs'):
                self.load_extension(admincog.replace('/', '.').replace('\\', '.'))
        except ClientException:
            log.critical('Could not load administrative cogs!')
        except ImportError:
            log.critical('Administrative cogs could not be imported!')
            traceback.print_exc()

    def register_nodes(self, nodes):
        for node in nodes:
            if node not in self.cfg['nodes']:
                self.cfg['nodes'][node] = None

    def register_cfg(self, cfg, prompt=None, defaultvalue=None):
        if cfg not in self.cfg['cogcfgs']:
            self.cfg['cogcfgs'][cfg] = (defaultvalue, prompt)

    async def get_context(self, message, *, cls=CharfredContext):
        return await super().get_context(message, cls=cls)

    async def on_command(self, ctx):
        log.info(f'[{ctx.author.name}]: {ctx.message.content}')

    async def on_ready(self):
        log.info(f'{self.user} reporting for duty!')
        log.info(f'ID: {self.user.id}')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.now()

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            is_owner = await self.is_owner(message.author)
            if not is_owner:
                return
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def close(self):
        log.info('Shutting down, this may take a couple seconds...')
        await super().close()
        log.info('Client disconnected.')
        await self.session.close()
        log.info('Session closed.')
        log.info('All done, goodbye sir!')

    def run(self, token=None):
        if token is None:
            log.info('Using pre-configured Token...')
            try:
                token = self.cfg['botToken']
            except KeyError:
                log.error('No token given, no token saved, abort!')
                return
        else:
            self.cfg['botToken'] = token
            self.cfg._save()
            log.info('Token saved for future use!')

        super().run(token, reconnect=True)


@click.command()
@click.option('--loglvl', default="DEBUG", help='Logging Level')
@click.option('--token', default=None, help='Discord Bot Token')
def run(loglvl, token):
    coloredlogs.install(level=loglvl,
                        logger=log,
                        fmt='%(asctime)s:%(msecs)03d [%(name)s]: %(levelname)s %(message)s')
    log.info('Initializing Charfred!')
    char = Charfred()
    char.run(token)
