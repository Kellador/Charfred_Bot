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
            currrole = n['role']
            if currrole:
                await ctx.send(f'Current minimum role for {node}: ```{currrole}```')
            else:
                await ctx.send(f'Everyone is free to use {node} commands!')
            if n['channels']:
                currChans = []
                for c in n['channels']:
                    currChans.append(self.bot.get_channel(c).mention)
                currChans = '\n'.join(currChans)
                await ctx.send(f'Current channels where {node} commands are permitted: ```{currChans}```')
            else:
                await ctx.send(f'{node} commands work everywhere!')

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
            r = await promptInput(ctx, 'Which would you like to edit? ``` role\n channels```')
            if r == 'role':
                role = await promptInput(ctx, 'Please enter the minimum role required'
                                         f' to use {node} commands.')
                self.botCfg['nodes'][node]['roles'] = role
            elif r == 'channels':
                chans = await promptInput(ctx, f'Enter all channels where you wish {node} to be allowed!'
                                          '\nDelimited only by spaces!')
                chans = list(map(int, chans.split()))
                self.botCfg['nodes'][node]['channels'] = chans
            else:
                await ctx.send(f'Invalid selection, aborting!')
                return

        await self.botCfg.save()
        await ctx.send(f'Edits to {node} saved successfully, hopefully...')


def setup(bot):
    bot.add_cog(admin(bot))
