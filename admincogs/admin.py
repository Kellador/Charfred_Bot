import logging
import datetime
from discord.ext import commands
from utils import Flipbook

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
        await ctx.sendmarkdown('# Locked and reloaded!')

    @commands.command(hidden=True)
    async def uptime(self, ctx):
        """Returns the current uptime."""

        currenttime = datetime.datetime.now()
        uptimedelta = currenttime - self.bot.uptime
        s = abs(int(uptimedelta.total_seconds()))
        d, s = divmod(s, 86400)
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        upstr = f'{d} day(s), {h} hour(s), {m} minute(s) and {s} second(s)'
        log.info(f'Up for {upstr}.')
        await ctx.sendmarkdown(f'# I have been up for {upstr}!')

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """Bot Prefix commands.

        This returns the list of all current prefixes,
        if no subcommand was given.
        """

        prefixes = '\n> '.join(self.cfg['prefixes'])
        await ctx.sendmarkdown('> Current prefixes: \n'
                               f'\t> {prefixes} \n> Mentioning {self.bot.user.name} works too!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def add(self, ctx, *, prefix: str):
        """Add a new prefix."""

        log.info(f'Adding a new prefix: {prefix}')
        self.cfg['prefixes'].append(prefix)
        await self.cfg.save()
        await ctx.sendmarkdown(f'# \'{prefix}\' has been registered!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def remove(self, ctx, *, prefix: str):
        """Remove a prefix."""

        log.info(f'Removing prefix: {prefix}')
        self.cfg['prefixes'].remove(prefix)
        await self.cfg.save()
        await ctx.sendmarkdown(f'# \'{prefix}\' has been unregistered!')

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
            await ctx.sendmarkdown(f'> {node} is not registered!')
            return

        role, _, timedout = await ctx.promptinput('# Please enter the minimum role required'
                                                  f' to use {node} commands.\nEnter "everyone"'
                                                  ' to have no role restriction.\n'
                                                  'Enter "owner_only" to restrict to bot owner.')
        if timedout:
            return
        if role == 'owner_only':
            self.cfg['nodes'][node] = None
        else:
            if role == 'everyone' or role == 'Everyone':
                role = '@everyone'
            self.cfg['nodes'][node] = role
        await self.cfg.save()
        log.info(f'{node} was edited.')
        await ctx.sendmarkdown(f'# Edits to {node} saved successfully!')

    @permissions.group(invoke_without_command=True, hidden=True)
    async def hierarchy(self, ctx):
        """Role hierarchy commands.

        This returns a list of all roles currently in the hierarchy,
        if no subcommand was given.

        Please note that the order within the hierarchy as listed here
        does not matter, in essence this hierarchy only sets which roles
        to take into consideration when checking for command permissions.

        That way you can have lower ranking members with special roles,
        that put them above higher ranking members in the guilds role
        hierarchy, but not have them inherit said higher ranking members
        command permissions, by just not adding that special role to this
        hierarchy.
        """

        log.info('Listing role hierarchy.')
        if not self.cfg['hierarchy']:
            await ctx.sendmarkdown('< No hierarchy set up! >')
        else:
            hierarchy = '\n'.join(self.cfg['hierarchy'])
            await ctx.sendmarkdown(f'# Role hierarchy:\n{hierarchy}')

    @hierarchy.command(hidden=True, name='add')
    @commands.is_owner()
    async def addtohierarchy(self, ctx, role):
        """Adds a role to the hierarchy."""

        if role in self.cfg['hierarchy']:
            await ctx.sendmarkdown(f'> {role} is already in the hierarchy.')
        else:
            log.info(f'Adding {role} to hierarchy.')
            self.cfg['hierarchy'].append(role)
            await self.cfg.save()
            await ctx.sendmarkdown(f'# {role} added to hierarchy.')

    @hierarchy.command(hidden=True, name='remove')
    @commands.is_owner()
    async def removefromhierarchy(self, ctx, role):
        """Removes a role from the hierarchy."""

        if role not in self.cfg['hierarchy']:
            await ctx.sendmarkdown(f'> {role} was not in hierarchy.')
        else:
            log.info(f'Removing {role} from hierarchy.')
            self.cfg['hierarchy'].remove(role)
            await self.cfg.save()
            await ctx.sendmarkdown(f'# {role} removed from hierarchy.')

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
            await ctx.sendmarkdown(f'> {cfg} is not registered!')
            return

        prompt = self.cfg['cogcfgs'][cfg][1]
        value, _, timedout = await ctx.promptinput(prompt)
        if timedout:
            return
        self.cfg['cogcfgs'][cfg] = (value, prompt)
        await self.cfg.save()
        log.info(f'{cfg} was edited.')
        await ctx.sendmarkdown(f'# Edits to {cfg} saved successfully!')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def debughook(self, ctx, hookurl: str=None):
        """Returns and/or changes webhook url used for debugging purposes."""

        if 'hook' in self.cfg and self.cfg['hook'] is not None:
            await ctx.sendmarkdown(f'> Current debug webhook:\n> {self.cfg["hook"]}')
        if hookurl:
            self.cfg['hook'] = hookurl
            await self.cfg.save()
            log.info('Changed debug webhook url.')
            await ctx.sendmarkdown(f'> Set debug webhook to:\n> {hookurl}')


def setup(bot):
    bot.add_cog(Admin(bot))
