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

    @commands.group(aliases=['cogs', 'gears', 'gear'])
    @_is_cmdChannel()
    @is_owner()
    async def cog(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @cog.command(aliases=['load', 'add'])
    @is_owner()
    async def loadcog(self, ctx, cogname: str):
        if self._loadcog(cogname):
            ctx.send(f'\"{cogname}\" loaded!')
        else:
            ctx.send(f'Could not load \"{cog}\"!\nMaybe you got the name wrong?')

    @cog.command(aliases=['unload', 'remove'])
    @is_owner()
    async def unloadcog(self, ctx, cogname: str):
        try:
            self.bot.unload_extension(cogname)
        except Exception as e:
            log.error(f'Could not unload \"{cogname}\"!')
            traceback.print_exc()
            ctx.send(f'Could not unload \"{cogname}\"!')
        else:
            ctx.send(f'\"{cogname}\" unloaded!')


def setup(bot):
    bot.add_cog(gearbox(bot))
