import asyncio
import datetime
import logging
import logging.handlers
import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional

import aiohttp
import click
import coloredlogs
from discord import ClientException, Intents
from discord.ext import commands

from utils import CharfredContext, Store

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
        super().__init__(
            command_prefix=_get_prefixes,
            description=description,
            pm_help=False,
            intents=Intents.all(),
        )
        self.dir = Path(__file__).parent
        self.cfg = Store(
            self.dir / 'configs/botCfg',
            ensure_entries=[
                ('prefix', {}),
                ('nodes', {'__core__': None}),
                ('hierarchy', []),
                ('cogcfgs', {}),
            ],
        )
        self.keywords = Store(
            self.dir / 'configs/keywords',
            boot_store=self.dir / 'configs/keywords_default',
        )

    def register_cfg(self, cfg, prompt=None, defaultvalue=None):
        if cfg not in self.cfg['cogcfgs']:
            self.cfg['cogcfgs'][cfg] = (defaultvalue, prompt)

    def register_core_cfg(self, config_option: str, defaultValue: Any = None):
        if config_option not in self.cfg:
            self.cfg[config_option] = defaultValue

    async def add_cog(self, cog: commands.Cog) -> None:
        if (cog_node := cog.qualified_name) not in self.cfg['nodes']:
            self.cfg['nodes'][cog_node] = {'__core__': None}

        for cmd in cog.get_commands():
            if (node := cmd.qualified_name) not in self.cfg['nodes'][cog_node]:
                self.cfg['nodes'][cog_node][node] = None

        return await super().add_cog(cog)

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

    async def setup_hook(self) -> None:
        loop = asyncio.get_event_loop()

        self.executor = ThreadPoolExecutor(thread_name_prefix='charfred')
        loop.set_default_executor(self.executor)

        self.session = aiohttp.ClientSession(loop=loop)

        try:
            os.chdir(self.dir)
            for admincog in _admincogs('admincogs'):
                await self.load_extension(admincog.replace('/', '.').replace('\\', '.'))
        except ClientException:
            log.critical('Could not load administrative cogs!')
        except ImportError:
            log.critical('Administrative cogs could not be imported!')
            traceback.print_exc()

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

        super().run(token, reconnect=True, log_handler=None)


@click.command()
@click.option('--loglvl', default="DEBUG", help='Logging Level')
@click.option('--token', default=None, help='Discord Bot Token')
def run(loglvl, token):
    logpath = Path(__file__).parent / 'logs'
    logpath.mkdir(exist_ok=True)

    filehandler = logging.handlers.RotatingFileHandler(
        f'{logpath}/charfred.log', maxBytes=32 * 1024 * 1024, backupCount=16
    )
    formatter = coloredlogs.ColoredFormatter(
        '%(asctime)s:%(msecs)03d [%(name)s]: %(levelname)s %(message)s'
    )
    filehandler.setFormatter(formatter)
    log.addHandler(filehandler)
    coloredlogs.install(
        level=loglvl,
        logger=log,
        fmt='%(asctime)s:%(msecs)03d [%(name)s]: %(levelname)s %(message)s',
    )

    dlog = logging.getLogger('discord')
    dlog.setLevel(logging.DEBUG)
    logging.getLogger('discord.http').setLevel(logging.INFO)
    dhandler = logging.handlers.RotatingFileHandler(
        f'{logpath}/discord.log', maxBytes=32 * 1024 * 1024, backupCount=8
    )
    dhandler.setFormatter(formatter)
    dlog.addHandler(dhandler)

    log.info('Initializing Charfred!')
    char = Charfred()
    char.run(token)
