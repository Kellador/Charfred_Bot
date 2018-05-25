import logging
from discord.ext import commands
from utils.discoutils import promptInput, promptConfirm

log = logging.getLogger('charfred')


class admin:
    def __init__(self, bot):
        self.bot = bot
        self.botCfg = bot.cfg

    @commands.group(invoke_without_command=True, hidden=True)
    async def prefix(self, ctx):
        """Bot Prefix operations.

        Without a subcommand, this returns the list
        of all current prefixes.
        """

        if ctx.invoked_subcommand is None:
            prefixes = ' '.join(self.botCfg['prefixes'])
            await ctx.send(f'Current prefixes: `{prefixes}`\n'
                           'Mentioning \@Charfred works too!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def add(self, ctx, prefix: str):
        """Add a new prefix."""

        log.info(f'Adding a new prefix: {prefix}')
        self.botCfg['prefixes'].append(prefix)
        await self.botCfg.save()
        await ctx.send(f'{prefix} has been registered!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def remove(self, ctx, prefix: str):
        """Remove a prefix."""

        log.info(f'Removing prefix: {prefix}')
        self.botCfg['prefixes'].remove(prefix)
        await self.botCfg.save()
        await ctx.send(f'{prefix} has been unregistered!')

    @commands.group(invoke_without_command=True, hidden=True, name='cmdChannel')
    @commands.is_owner()
    async def defaultCmdCh(self, ctx):
        """Command channel operations.

        Without a subncommand, this shows the default command channel
        where all commands are permitted to be executed,
        regardless of specified channels in their respective
        permission nodes.
        """

        if ctx.invoked_subcommand is None:
            defCC = self.bot.get_channel(self.botCfg['defaultCmdCh']).mention
            await ctx.send(f'Current default command channel: {defCC}')

    @defaultCmdCh.command(hidden=True, name='set')
    @commands.is_owner()
    async def setDefaultCmdCh(self, ctx, ch: int):
        newDCC = self.bot.get_channel(ch)
        if newDCC is None:
            await ctx.send('Invalid channel id, please try again!')
        else:
            self.botCfg['defaultCmdCh'] = ch
            await self.botCfg.save()
            await ctx.send(f'Default command channel set to {newDCC.mention}!')

    @commands.group(invoke_without_command=True, hidden=True)
    async def permissions(self, ctx):
        """Permission and special settings operations.

        Without a subcommand, this returns a list
        of all current permission nodes.
        """

        if ctx.invoked_subcommand is None:
            nodeList = '\n'.join(list(self.botCfg['nodes']))
            await ctx.send(f'Current permission nodes:\n```{nodeList}```\n'
                           '\'spec\' signifies special permission nodes.')

    @permissions.command(hidden=True)
    @commands.is_owner()
    async def list(self, ctx, node: str):
        """List current state of a node."""

        if node not in self.botCfg['nodes']:
            await ctx.send(f'{node} is not registered!')
            return

        n = self.botCfg['nodes'][node]
        if node.startswith('spec:'):
            if type(n[0]) is str:
                await ctx.send(f'{n[-1]}: {n[0]}')
            else:
                await ctx.send(f'{n[-1]}: {str(n[0])}')
        else:
            currRanks = '\n'.join(n['ranks'])
            await ctx.send(f'Current ranks with permission for {node}: ```{currRanks}```')
            currChans = '\n'.join(n['channels'])
            await ctx.send(f'Current channels where {node} is permitted: ```{currChans}```')

    @permissions.command(hidden=True)
    @commands.is_owner()
    async def edit(self, ctx, node: str):
        """Edit a permission node."""

        if node not in self.botCfg['nodes']:
            await ctx.send(f'{node} is not registered!')
            return

        n = self.botCfg['nodes'][node]
        if node.startswith('spec:'):
            if type(n[0]) is str:
                spec = await promptInput(ctx, n[-1])
            elif type(n[0]) is bool:
                spec = await promptConfirm(ctx, n[-1])
            else:
                await ctx.send(f'{node} is misconfigured; Only str and bool types'
                               'are supported at the moment!')
                return
            self.botCfg['nodes'][node] = [spec, n[-1]]
        else:
            opts = '\n'.join(n)
            r = await promptInput(ctx, f'Which would you like to edit?\n```{opts}```')
            if r == 'ranks':
                ranks = await promptInput(ctx, 'Please enter all ranks, which should be permitted'
                                          f'to use {node}.'
                                          '\nSeperated by spaces only!')
                self.botCfg['nodes'][node]['ranks'] = ranks.split()
            elif r == 'channels':
                chans = await promptInput(ctx, f'Enter all channels where you wish {node} to be allowed!'
                                          '\nDelimited only by spaces!')
                chans = chans.split().map(int, chans)
                self.botCfg['nodes'][node]['channels'] = chans
            else:
                await ctx.send(f'Invalid selection, aborting!')
                return

        await self.botCfg.save()
        await ctx.send(f'Edits to {node} saved successfully, hopefully...')


def setup(bot):
    bot.add_cog(admin(bot))
