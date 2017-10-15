import logging
import traceback
from discord.ext import commands
from .utils.config import Config
from .utils.discoutils import is_owner, _is_cmdChannel

log = logging.getLogger('charfred')


class gearbox:
    def __init__(self, bot):
        self.bot = bot
        self.dir = bot.dir
        self.loop = bot.loop
        self.cogfig = Config(f'{self.dir}/cogs/configs/cogCfg.json',
                             load=True, loop=self.loop)
        for cog in self.cogfig['cogs']:
            self._loadcog(cog)

    def _loadcog(self, cog):
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

    @commands.group(hidden=True, aliases=['cogs', 'gears', 'gear'])
    @_is_cmdChannel()
    @is_owner()
    async def cog(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @cog.command(aliases=['load', 'add'])
    @is_owner()
    async def loadcog(self, ctx, cogname: str):
        if self._loadcog(cogname):
            await ctx.send(f'\"{cogname}\" loaded!')
        else:
            await ctx.send(f'Could not load \"{cogname}\"!\nMaybe you got the name wrong?')

    @cog.command(aliases=['unload', 'remove'])
    @is_owner()
    async def unloadcog(self, ctx, cogname: str):
        if self._unload(cogname):
            await ctx.send(f'\"{cogname}\" unloaded!')
        else:
            await ctx.send(f'Could not unload \"{cogname}\"!')

    @commands.command(hidden=True)
    @is_owner()
    async def takeavacation(self, ctx):
        await ctx.send('As you wish sir!')
        try:
            self.loop.run_until_complete(self.bot.logout())
        finally:
            self.loop.close()


def setup(bot):
    bot.add_cog(gearbox(bot))
