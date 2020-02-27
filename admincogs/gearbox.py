import logging
import traceback
from pathlib import Path
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded, ExtensionNotFound, \
    NoEntryPointError, ExtensionFailed, ExtensionAlreadyLoaded
from utils import Config

log = logging.getLogger('charfred')


class Gearbox(commands.Cog):
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

    def _dotify(self, path):
        return path.relative_to(self.dir).stem.replace('/', '.')

    def _searchpaths(self, cogname):
        maybedots = Path('/'.join(cogname.split('.')))
        matches = list(self.dir.rglob(f'{maybedots}.py'))
        if matches:
            if len(matches) > 1:
                return list(map(self._dotify, matches))
            else:
                return self._dotify(matches[0])
        else:
            return None

    def _searchloaded(self, cogname):
        loaded = list(self.bot.extensions)
        matches = [cog for cog in loaded if cogname in cog]
        if matches:
            if len(matches) > 1:
                return matches
            else:
                return matches[0]
        else:
            return None

    def _load(self, cog, search=True):
        try:
            self.bot.load_extension(cog)
        except ExtensionAlreadyLoaded:
            status = (False, f'Could not load "{cog}", already loaded!')
            log.warning(status[1])
        except ExtensionNotFound:
            if search:
                candidates = self._searchpaths(cog)
                if candidates:
                    if isinstance(candidates, list):
                        status = (False, f'Found multiple matching cogs: >\n' +
                                  "\n".join(candidates) +
                                  '\n< Please be more specific!')
                        log.info('Direct load failed, search inconclusive.')
                    else:
                        self._load(candidates, search=False)
                else:
                    status = (False, f'Could not load "{cog}", search yielded no matches!')
                    log.info('Direct load failed, search yielded no matches.')
            else:
                status = (False, f'Could not load "{cog}", not found!')
                log.info(status[1])
        except ExtensionFailed:
            status = (False, f'Exception occurred when loading "{cog}"!')
            traceback.print_exc()
            log.error(status[1])
        except NoEntryPointError:
            status = (False, f'"{cog}" does not have a setup function!')
            log.warning(status[1])
        else:
            status = (True, f'"{cog}" reloaded!')
            log.info(status[1])
        return status

    def _unload(self, cog, search=True):
        try:
            self.bot.unload_extension(cog)
        except ExtensionNotLoaded:
            if search:
                candidates = self._searchloaded(cog)
                if candidates:
                    if isinstance(candidates, list):
                        status = (False, f'Found multiple matching cogs: >\n' +
                                  "\n".join(candidates) +
                                  '\n< Please be more specific!')
                        log.info('Direct unload failed, search inconclusive.')
                    else:
                        self._unload(candidates, search=False)
                else:
                    status = (False, f'Could not unload "{cog}", search yielded no matches!')
                    log.info('Direct unload failed, search yielded no matches.')
            else:
                status = (False, f'Could not unload "{cog}", not loaded!')
                log.warning(status[1])
        else:
            status = (True, f'"{cog}" unloaded!')
            log.info(status[1])
        return status

    def _reload(self, cog, search=True):
        try:
            self.bot.reload_extension(cog)
        except ExtensionNotLoaded:
            status = (False, f'Could not reload "{cog}", not loaded!')
            log.warning(status[1])
        except ExtensionNotFound:
            if search:
                candidates = self._searchloaded(cog)
                if candidates:
                    if isinstance(candidates, list):
                        status = (False, f'Found multiple matching cogs: >\n' +
                                  "\n".join(candidates) +
                                  '\n< Please be more specific!')
                        log.info('Direct unload failed, search inconclusive.')
                    else:
                        self._unload(candidates, search=False)
                else:
                    status = (False, f'Could not reload "{cog}", search yielded no matches!')
                    log.info('Direct unload failed, search yielded no matches.')
            else:
                status = (False, f'Could not unload "{cog}", not loaded!')
                log.warning(status[1])
        except ExtensionFailed:
            status = (False, f'Exception occurred when loading "{cog}"!')
            traceback.print_exc()
            log.error(status[1])
        except NoEntryPointError:
            status = (False, f'"{cog}" does not have a setup function!')
            log.warning(status[1])
        else:
            status = (True, f'"{cog}" reloaded!')
            log.info(status[1])
        return status

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
                if c.startswith('admincogs.'):
                    adminCogMsgs.append(f'# {c}')
                    continue
                statusMsgs.append(f'< {c} >')
        statusMsgs.append('\n> Cogs not being loaded on startup are marked in yellow.')
        shouldMsgs = []
        shouldMsgs.append('\nCogs that should have loaded on startup, '
                          'but are currently unloaded:\n')
        for c in startupCogs:
            if c in activeCogs:
                continue
            else:
                shouldMsgs.append(f'> {c}')
        if len(shouldMsgs) > 1:
            statusMsgs.extend(shouldMsgs)
        statusMsgs = '\n'.join(statusMsgs)
        adminCogMsgs = '\n'.join(adminCogMsgs)
        await ctx.sendmarkdown(f'Cogs currently loaded:\n{statusMsgs}\n'
                               f'Essential Cogs:\n{adminCogMsgs}')

    @cog.command(aliases=['current-to-startup'])
    @commands.is_owner()
    async def addloaded(self, ctx):
        """Adds all currently loaded cogs to be loaded on startup."""

        for cogname in list(self.bot.extensions):
            if cogname in self.cogfig['cogs']:
                continue
            if cogname.startswith('admincogs.'):
                continue
            self.cogfig['cogs'].append(cogname)
        else:
            await self.cogfig.save()
            cogList = '\n# '.join(self.cogfig['cogs'])
            await ctx.sendmarkdown(f'# Cogs being loaded on startup:\n# {cogList}')

    @cog.command(name='load')
    @commands.is_owner()
    async def loadcog(self, ctx, cogname: str):
        """Load a cog."""

        success, reply = self._load(cogname)
        await ctx.sendmarkdown(f'# {reply}' if success else f'< {reply} >')

    @cog.command(name='unload')
    @commands.is_owner()
    async def unloadcog(self, ctx, cogname: str):
        """Unload a cog."""

        success, reply = self._unload(cogname)
        await ctx.sendmarkdown(f'# {reply}' if success else f'< {reply} >')

    @cog.command(name='reload')
    @commands.is_owner()
    async def reloadcog(self, ctx, cogname: str):
        """Reload a cog."""

        success, reply = self._reload(cogname)
        await ctx.sendmarkdown(f'# {reply}' if success else f'< {reply} >')

    @cog.command(name='reinitiate')
    @commands.is_owner()
    async def reinitiatecogs(self, ctx):
        """Reloads all cogs, but the admincogs."""

        out = ["# Reinitiation:"]
        for cog in list(self.bot.extensions):
            if not cog.startswith('admincogs'):
                success, reply = self._reload(cog)
                out.append(f'# {reply}' if success else f'< {reply} >')
        if len(out) > 1:
            await ctx.sendmarkdown('\n'.join(out))
        else:
            await ctx.sendmarkdown('< No non-admin cogs to reload! >')

    @cog.command(name='add')
    @commands.is_owner()
    async def addcog(self, ctx, cogname: str):
        """Adds a cog to be loaded on startup."""

        if cogname.startswith('admincogs.'):
            return
        if cogname in self.cogfig['cogs']:
            await ctx.sendmarkdown(f'> \"{cogname}\" already loading on startup!')
            return
        success, reply = self._load(cogname)
        if success:
            self.cogfig['cogs'].append(cogname)
            await self.cogfig.save()
            await ctx.sendmarkdown(f'# \"{cogname}\" will now be loaded automatically.')
        await ctx.sendmarkdown(f'# {reply}' if success else f'< {reply} >')

    @cog.command(name='remove')
    @commands.is_owner()
    async def removecog(self, ctx, cogname: str):
        """Removes a cog from being loaded on startup."""

        try:
            self.cogfig['cogs'].remove(cogname)
        except ValueError:
            await ctx.sendmarkdown(f'> {cogname} was not set to load on startup.')
        else:
            await self.cogfig.save()
            await ctx.sendmarkdown(f'# \"{cogname}\" will no longer be loaded automatically.')
        success, reply = self._unload(cogname)
        await ctx.sendmarkdown(f'# {reply}' if success else f'< {reply} >')

    @cog.command(aliases=[''])
    @commands.is_owner()
    async def clear(self, ctx):
        """Removes all cogs, except admincogs,
        from being loaded on startup and unloads them.
        """

        for cog in list(self.bot.extensions):
            if cog.startswith('admincogs.'):
                continue
            self._unload(cog, search=False)
            self.cogfig['cogs'].remove(cog)
        else:
            await self.cogfig.save()
            await ctx.sendmarkdown('# Done!')


def setup(bot):
    bot.add_cog(Gearbox(bot))
