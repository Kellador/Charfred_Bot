import logging
from discord.ext import commands
from utils.discoutils import promptInput, promptConfirm, sendMarkdown
from utils.flipbooks import NodeFlipbook

log = logging.getLogger('charfred')


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self.botCfg = bot.cfg

    @commands.command(hidden=True)
    @commands.is_owner()
    async def cfgreload(self, ctx):
        """Reload botCfg.

        Useful when you edited botCfg.json
        manually or with Charwizard.
        Will discard all unsaved changes!
        """

        log.info('Reloading botCfg.json...')
        await self.botCfg.load()
        log.info('Reloaded!')
        await sendMarkdown(ctx, '# Locked and reloaded!')

    @commands.group(invoke_without_command=True, hidden=True)
    async def prefix(self, ctx):
        """Bot Prefix operations.

        Without a subcommand, this returns the list
        of all current prefixes.
        """

        prefixes = '\n\t> '.join(self.botCfg['prefixes'])
        await sendMarkdown(ctx, '> Current prefixes: \n'
                           f'\t> {prefixes} \n> Mentioning \@Charfred works too!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def add(self, ctx, *, prefix: str):
        """Add a new prefix."""

        log.info(f'Adding a new prefix: {prefix}')
        self.botCfg['prefixes'].append(prefix)
        await self.botCfg.save()
        await sendMarkdown(ctx, f'# \'{prefix}\' has been registered!')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def remove(self, ctx, *, prefix: str):
        """Remove a prefix."""

        log.info(f'Removing prefix: {prefix}')
        self.botCfg['prefixes'].remove(prefix)
        await self.botCfg.save()
        await sendMarkdown(ctx, f'# \'{prefix}\' has been unregistered!')

    @commands.group(invoke_without_command=True, hidden=True, aliases=['perms'])
    async def permissions(self, ctx):
        """Permission and special settings operations.

        Without a subcommand, this returns a list
        of all current permission nodes.
        """

        nodeList = '\n\t> '.join(list(self.botCfg['nodes']))
        await sendMarkdown(ctx, '> Current permission nodes:\n'
                           f'\t> {nodeList}\n> \'spec\' signifies special permission nodes.')

    @permissions.command(hidden=True)
    @commands.is_owner()
    async def nodeBook(self, ctx):
        """Opens the Permission Node Book."""

        nodeFlip = NodeFlipbook(ctx, self.botCfg)
        await nodeFlip.flip()

    @permissions.command(hidden=True)
    async def list(self, ctx, node: str):
        """List current state of a node."""

        if node not in self.botCfg['nodes']:
            await sendMarkdown(ctx, f'< {node} is not registered! >')
            return

        n = self.botCfg['nodes'][node]
        if node.startswith('spec:'):
            if type(n[0]) is str:
                await sendMarkdown(ctx, f'> {n[-1]}: {n[0]}')
            else:
                await sendMarkdown(ctx, f'> {n[-1]}: {str(n[0])}')
        else:
            currrole = n['role']
            if currrole:
                await sendMarkdown(ctx, f'> Current minimum role for {node}:\n'
                                   f'\t> {currrole}')
            else:
                await sendMarkdown(ctx, f'> Everyone is free to use {node} commands!')
            if n['channels']:
                currChans = []
                for c in n['channels']:
                    currChans.append(self.bot.get_channel(c).mention)
                currChans = '\n\t> '.join(currChans)
                await sendMarkdown(ctx, f'> Current channels where {node} commands are'
                                   ' permitted:')
                await ctx.send(f'{currChans}')
            else:
                await sendMarkdown(ctx, f'> {node} commands work everywhere!')

    @permissions.command(hidden=True)
    @commands.is_owner()
    async def edit(self, ctx, node: str):
        """Edit a permission node."""

        if node not in self.botCfg['nodes']:
            await sendMarkdown(ctx, f'> {node} is not registered!')
            return

        n = self.botCfg['nodes'][node]
        if node.startswith('spec:'):
            if type(n[0]) is str:
                spec, _, _ = await promptInput(ctx, f'# {n[-1]}')
            elif type(n[0]) is bool:
                spec, _, _ = await promptConfirm(ctx, f'# {n[-1]}')
            else:
                await sendMarkdown(ctx, f'< {node} is misconfigured; Only str and bool types'
                                   'are supported at the moment! >')
                return
            self.botCfg['nodes'][node] = [spec, n[-1]]
        else:
            r, _, _ = await promptInput(ctx, '# Which would you like to edit?\n\trole\n\tchannels')
            if r == 'role':
                role, _, _ = await promptInput(ctx, '# Please enter the minimum role required'
                                               f' to use {node} commands.')
                self.botCfg['nodes'][node]['role'] = role
            elif r == 'channels':
                chans, _, _ = await promptInput(ctx, f'# Enter all channels where you wish {node} to be '
                                                ' allowed!\n# Delimited only by spaces!')
                chans = list(map(int, chans.split()))
                self.botCfg['nodes'][node]['channels'] = chans
            else:
                await sendMarkdown(ctx, '< Invalid selection, aborting! >')
                return

        await self.botCfg.save()
        await sendMarkdown(ctx, f'# Edits to {node} saved successfully!')


def setup(bot):
    bot.add_cog(Admin(bot))
