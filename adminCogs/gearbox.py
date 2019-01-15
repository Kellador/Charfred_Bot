import logging
import traceback
from discord.ext import commands
from utils.config import Config
from utils.discoutils import sendMarkdown

log = logging.getLogger('charfred')


class Gearbox:
    def __init__(self, bot):
        self.bot = bot
        self.dir = bot.dir
        self.loop = bot.loop
        self.cogfig = Config(f'{self.dir}/configs/cogCfg.json',
                             load=True, loop=self.loop)
        try:
            for cog in self.cogfig['cogs']:
                self._load(cog)
        except KeyError:
            log.info('No cog configurations exist. Initializing empty config.')
            self.cogfig['cogs'] = []

    def _load(self, cog):
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            log.error(f'Could not load \"{cog}\"!')
            traceback.print_exc()
            return False
        else:
            log.info(f'\"{cog}\" loaded!')
            return True

    def _unload(self, cog):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            log.error(f'Could not unload \"{cog}\"!')
            traceback.print_exc()
            return False
        else:
            log.info(f'\"{cog}\" unloaded!')
            return True

    def _reload(self, cog):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            log.error(f'Could not reload \"{cog}\"!')
            traceback.print_exc()
            return False
        else:
            log.info(f'\"{cog}\" reloaded!')
            return True

    @commands.group(hidden=True, aliases=['extension', 'cogs'], invoke_without_command=True)
    @commands.is_owner()
    async def cog(self, ctx):
        """Cog commands.

        This returns a list of all active and inactive cogs,
        including their status on whether they load on startup or not,
        if no subcommand was given.
        """

        activeCogs = list(self.bot.extensions)
        startupCogs = self.cogfig['cogs']
        statusMsgs = []
        adminCogMsgs = []
        for c in activeCogs:
            if c in startupCogs:
                statusMsgs.append(f'# {c}')
            else:
                if c.startswith('adminCogs.'):
                    adminCogMsgs.append(f'# {c}')
                    continue
                statusMsgs.append(f'< {c} >')
        statusMsgs.append('\n> Cogs not being loaded on startup are marked in yellow.')
        statusMsgs.append('\n# Cogs that should have loaded on startup, '
                          'but are currently unloaded:\n')
        for c in startupCogs:
            if c in activeCogs:
                continue
            else:
                statusMsgs.append(f'> {c}')
        statusMsgs = '\n'.join(statusMsgs)
        adminCogMsgs = '\n'.join(adminCogMsgs)
        await sendMarkdown(ctx, f'# Cogs currently loaded:\n{statusMsgs}\n'
                           f'Essential Cogs:\n{adminCogMsgs}')

    @cog.command(aliases=['current-to-startup'])
    @commands.is_owner()
    async def addloaded(self, ctx):
        """Adds all currently loaded cogs to be loaded on startup."""

        for cogname in list(self.bot.extensions):
            if cogname in self.cogfig['cogs']:
                continue
            if cogname.startswith('adminCogs.'):
                continue
            self.cogfig['cogs'].append(cogname)
        else:
            await self.cogfig.save()
            cogList = '\n# '.join(self.cogfig['cogs'])
            await sendMarkdown(ctx, f'# Cogs being loaded on startup:\n# {cogList}')

    @cog.command(name='load')
    @commands.is_owner()
    async def loadcog(self, ctx, cogname: str):
        """Load a cog."""

        if self._load(cogname):
            await sendMarkdown(ctx, f'# \"{cogname}\" loaded!')
        else:
            await sendMarkdown(ctx, f'< Could not load \"{cogname}\"! '
                               'Maybe you got the name wrong? >')

    @cog.command(name='unload')
    @commands.is_owner()
    async def unloadcog(self, ctx, cogname: str):
        """Unload a cog."""

        if self._unload(cogname):
            await sendMarkdown(ctx, f'# \"{cogname}\" unloaded!')
        else:
            await sendMarkdown(ctx, f'< Could not unload \"{cogname}\"! >'
                               'Maybe it is already unloaded? >')

    @cog.command(name='reload')
    @commands.is_owner()
    async def reloadcog(self, ctx, cogname: str):
        """Reload a cog."""

        if self._reload(cogname):
            await sendMarkdown(ctx, f'# \"{cogname}\" reloaded!')
        else:
            await sendMarkdown(ctx, f'< Could not reload \"{cogname}\"! >')

    @cog.command(name='reinitiate')
    @commands.is_owner()
    async def reinitiatecogs(self, ctx):
        """Reloads all cogs, but the adminCogs."""

        for cog in list(self.bot.extensions):
            if not cog.startswith('adminCogs'):
                self._unload(cog)
        for cog in self.cogfig['cogs']:
            self._load(cog)

    @cog.command(name='add')
    @commands.is_owner()
    async def addcog(self, ctx, cogname: str):
        """Adds a cog to be loaded on startup."""

        if cogname.startswith('adminCogs.'):
            return
        if cogname in self.cogfig['cogs']:
            await sendMarkdown(ctx, f'> \"{cogname}\" already loading on startup!')
            return
        self.cogfig['cogs'].append(cogname)
        await self.cogfig.save()
        await sendMarkdown(ctx, f'# \"{cogname}\" will now be loaded automatically.')
        if self._load(cogname):
            await sendMarkdown(ctx, f'# \"{cogname}\" loaded!')
        else:
            await sendMarkdown(ctx, f'< Could not load \"{cogname}\"! '
                               'Maybe you got the name wrong? >')

    @cog.command(name='remove')
    @commands.is_owner()
    async def removecog(self, ctx, cogname: str):
        """Removes a cog from being loaded on startup."""

        self.cogfig['cogs'].remove(cogname)
        await self.cogfig.save()
        await sendMarkdown(ctx, f'# \"{cogname}\" will no longer be loaded automatically.')
        if self._unload(cogname):
            await sendMarkdown(ctx, f'# \"{cogname}\" unloaded!')
        else:
            await sendMarkdown(ctx, f'< Could not unload \"{cogname}\"! '
                               'Maybe it is already unloaded? >')

    @cog.command(aliases=[''])
    @commands.is_owner()
    async def clear(self, ctx):
        """Removes all cogs from being loaded on startup and unloads all cogs."""

        for cog in list(self.bot.extensions):
            if cog.startswith('adminCogs.'):
                continue
            self._unload(cog)
            self.cogfig['cogs'].remove(cog)
        else:
            await sendMarkdown(ctx, '# Done!')


def setup(bot):
    bot.add_cog(Gearbox(bot))
