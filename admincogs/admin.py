import logging
import datetime
from discord.ext import commands
from utils.discoutils import promptinput, sendmarkdown
from utils.flipbooks import Flipbook

log = logging.getLogger('charfred')


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cfg = bot.cfg

    @commands.command(hidden=True)
    @commands.is_owner()
    async def cfgreload(self, ctx):
        """Reload cfg.

        Useful when you edited botcfg.json
        manually.
        Will discard all unsaved changes!
        """

        log.info('Reloading botcfg.json...')
        await self.cfg.load()
        log.info('Reloaded!')
        await sendmarkdown(ctx, '# Locked and reloaded!')

    @commands.command(hidden=True)
    async def uptime(self, ctx):
        """Returns the current uptime."""

        currenttime = datetime.datetime.now()
        uptimedelta = currenttime - self.bot.uptime
        s = abs(int(uptimedelta.total_seconds()))
        d, s = divmod(s, 86400)
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        upstr = f'{d} days, {h} hours, {m} minutes and {s} seconds'
        log.info(f'Up for {upstr}.')
        await sendmarkdown(ctx, f'# I have been up for {upstr}!')

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """Bot Prefix commands.

        This returns the list of all current prefixes,
        if no subcommand was given.
        """

        prefixes = '\n> '.join(self.cfg['prefixes'])
        await sendmarkdown(ctx, '> Current prefixes: \n'
                           f'\t> {prefixes} \n> Mentioning {self.bot.user.name} works too!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def add(self, ctx, *, prefix: str):
        """Add a new prefix."""

        log.info(f'Adding a new prefix: {prefix}')
        self.cfg['prefixes'].append(prefix)
        await self.cfg.save()
        await sendmarkdown(ctx, f'# \'{prefix}\' has been registered!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def remove(self, ctx, *, prefix: str):
        """Remove a prefix."""

        log.info(f'Removing prefix: {prefix}')
        self.cfg['prefixes'].remove(prefix)
        await self.cfg.save()
        await sendmarkdown(ctx, f'# \'{prefix}\' has been unregistered!')

    def _parserole(self, role):
        if not role:
            return 'Owner only'
        else:
            return role

    @commands.group(invoke_without_command=True, hidden=True, aliases=['perms'])
    async def permissions(self, ctx):
        """Permission commands.

        This returns a list of all current permission nodes
        and their minimum required role, if no subcommand was given.
        """

        log.info('Listing permission nodes.')
        nodelist = list(self.cfg['nodes'].items())
        nodelist.sort()
        nodeentries = [f'{k}:\n\t{self._parserole(v)}' for k, v in nodelist]
        nodeflip = Flipbook(ctx, nodeentries, entries_per_page=12,
                            title='Permission Nodes', close_on_exit=True)
        await nodeflip.flip()

    @permissions.command(hidden=True)
    @commands.is_owner()
    async def edit(self, ctx, node: str):
        """Edit a permission node."""

        if node not in self.cfg['nodes']:
            await sendmarkdown(ctx, f'> {node} is not registered!')
            return

        role, _, timedout = await promptinput(ctx, '# Please enter the minimum role required'
                                              f' to use {node} commands.\nEnter "everyone"'
                                              ' to have no role restriction.')
        if timedout:
            return
        if role == 'everyone' or role == 'Everyone':
            role = '@everyone'
        self.cfg['nodes'][node] = role
        await self.cfg.save()
        log.info(f'{node} was edited.')
        await sendmarkdown(ctx, f'# Edits to {node} saved successfully!')

    @commands.group(invoke_without_command=True, hidden=True, aliases=['cogcfgs'])
    @commands.is_owner()
    async def cogcfg(self, ctx):
        """Cog-specific configuration commands.

        This returns a list of all currently known cog-specific
        configurations and their current values, if no subcommand was given.
        """

        log.info('Listing cog specific configurations.')
        cogcfgs = list(self.cfg['cogcfgs'].items())
        cogcfgs.sort()
        cogcfgentries = [f'{k}:\n\t{v[0]}' for k, v in cogcfgs]
        cogcfgflip = Flipbook(ctx, cogcfgentries, entries_per_page=12,
                              title='Cog-specific Configurations')
        await cogcfgflip.flip()

    @cogcfg.command(hidden=True, name='edit')
    async def cogcfgedit(self, ctx, cfg: str):
        """Edit cog-specific configuration."""

        if cfg not in self.cfg['cogcfgs']:
            await sendmarkdown(ctx, f'> {cfg} is not registered!')
            return

        prompt = self.cfg['cogcfgs'][cfg][1]
        value, _, timedout = await promptinput(ctx, prompt)
        if timedout:
            return
        self.cfg['cogcfgs'][cfg] = (value, prompt)
        await self.cfg.save()
        log.info(f'{cfg} was edited.')
        await sendmarkdown(ctx, f'# Edits to {cfg} saved successfully!')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def debughook(self, ctx, hookurl: str=None):
        """Returns and/or changes webhook url used for debugging purposes."""

        if 'hook' in self.cfg and self.cfg['hook'] is not None:
            await sendmarkdown(ctx, f'> Current debug webhook:\n> {self.cfg["hook"]}')
        if hookurl:
            self.cfg['hook'] = hookurl
            await self.cfg.save()
            log.info('Changed debug webhook url.')
            await sendmarkdown(ctx, f'> Set debug webhook to:\n> {hookurl}')


def setup(bot):
    bot.add_cog(Admin(bot))
