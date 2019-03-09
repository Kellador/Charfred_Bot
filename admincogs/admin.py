import logging
import datetime
from discord.ext import commands
from utils.discoutils import promptInput, sendMarkdown
from utils.flipbooks import Flipbook

log = logging.getLogger('charfred')


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.botcfg = bot.cfg

    @commands.command(hidden=True)
    @commands.is_owner()
    async def cfgreload(self, ctx):
        """Reload botcfg.

        Useful when you edited botcfg.json
        manually.
        Will discard all unsaved changes!
        """

        log.info('Reloading botcfg.json...')
        await self.botcfg.load()
        log.info('Reloaded!')
        await sendMarkdown(ctx, '# Locked and reloaded!')

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
        await sendMarkdown(ctx, '# I have been up for {upstr}!')

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """Bot Prefix commands.

        This returns the list of all current prefixes,
        if no subcommand was given.
        """

        prefixes = '\n> '.join(self.botcfg['prefixes'])
        await sendMarkdown(ctx, '> Current prefixes: \n'
                           f'\t> {prefixes} \n> Mentioning {self.bot.user.name} works too!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def add(self, ctx, *, prefix: str):
        """Add a new prefix."""

        log.info(f'Adding a new prefix: {prefix}')
        self.botcfg['prefixes'].append(prefix)
        await self.botcfg.save()
        await sendMarkdown(ctx, f'# \'{prefix}\' has been registered!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def remove(self, ctx, *, prefix: str):
        """Remove a prefix."""

        log.info(f'Removing prefix: {prefix}')
        self.botcfg['prefixes'].remove(prefix)
        await self.botcfg.save()
        await sendMarkdown(ctx, f'# \'{prefix}\' has been unregistered!')

    def _parserole(role):
        if not role:
            return 'Owner only'
        else:
            return role

    @commands.group(invoke_without_command=True, hidden=True, aliases=['perms'])
    async def permissions(self, ctx):
        """Permission and special settings commands.

        This returns a list of all current permission nodes,
        if no subcommand was given.
        """

        log.info('Listing permission nodes.')
        nodelist = list(self.botcfg['nodes'].items())
        nodelist.sort()
        nodeentries = [f'{k}:\n\t{self._parserole(v)}' for k, v in nodelist]
        nodeentries = '\n'.join(nodeentries)
        nodeflip = Flipbook(ctx, nodeentries, entries_per_page=12,
                            title='Permission Nodes')
        await nodeflip.flip()

    @permissions.command(hidden=True)
    @commands.is_owner()
    async def edit(self, ctx, node: str):
        """Edit a permission node."""

        if node not in self.botcfg['nodes']:
            await sendMarkdown(ctx, f'> {node} is not registered!')
            return

        role, _, timedout = await promptInput(ctx, '# Please enter the minimum role required'
                                              f' to use {node} commands.\nEnter "everyone"'
                                              ' to have no role restriction.')
        if timedout:
            return
        if role == 'everyone' or role == 'Everyone':
            role = '@everyone'
        self.botcfg['nodes'][node] = role
        await self.botcfg.save()
        log.info(f'{node} was edited.')
        await sendMarkdown(ctx, f'# Edits to {node} saved successfully!')

    @commands.command()
    @commands.is_owner()
    async def debughook(self, ctx, hookurl: str=None):
        """Returns and/or changes webhook url used for debugging purposes."""

        if 'hook' in self.botcfg and self.botcfg['hook'] is not None:
            await sendMarkdown(ctx, f'> Current debug webhook:\n> {self.botcfg["hook"]}')
        if hookurl:
            self.botcfg['hook'] = hookurl
            await self.botcfg.save()
            log.info('Changed debug webhook url.')
            await sendMarkdown(ctx, f'> Set debug webhook to:\n> {hookurl}')


def setup(bot):
    bot.add_cog(Admin(bot))
