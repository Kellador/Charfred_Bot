import logging
import datetime
from time import time
import discord
from discord.ext import commands
from utils import Flipbook, SelectionView
from utils.permissions import PermissionLevel

log = logging.getLogger(f'charfred.{__name__}')


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

        is_owner = await self.bot.is_owner(ctx.author)
        if is_owner:
            out = []
            for guild_id, prefixes in self.cfg['prefix'].items():
                guild = self.bot.get_guild(int(guild_id))
                out.append(f'# {guild.name}:' if guild else f'# {guild_id}:')
                out.extend([f'\t {prefix}' for prefix in prefixes])
        elif ctx.guild:
            out = self.cfg['prefix'][str(ctx.guild.id)]
        else:
            out = []
        out.extend(
            [
                '# Bot mentions (always work):',
                f'<@{self.bot.user.id}> ',
                f'<@!{self.bot.user.id}> ',
                '> There\'s a space after the mentions which is part of the prefix!',
            ]
        )
        out = '\n'.join(out)
        await ctx.sendmarkdown(f'# Current prefixes:\n{out}')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def add(self, ctx, *, prefix: str):
        """Add a new prefix."""

        if ctx.guild:
            log.info(f'Adding a new prefix: {prefix}')

            try:
                self.cfg['prefix'][str(ctx.guild.id)].append(prefix)
            except KeyError:
                self.cfg['prefix'][str(ctx.guild.id)] = [prefix]

            await self.cfg.save()
            await ctx.sendmarkdown(f'# \'{prefix}\' has been registered!')
        else:
            await ctx.sendmarkdown('< Cannot save prefixes outside of a guild! >')

    @prefix.command(hidden=True)
    @commands.is_owner()
    async def remove(self, ctx, *, prefix: str):
        """Remove a prefix."""

        if ctx.guild:
            log.info(f'Removing prefix: {prefix}')

            try:
                self.cfg['prefix'][str(ctx.guild.id)].remove(prefix)
            except KeyError:
                await ctx.sendmarkdown('< This guild has no saved prefixes. >')
            except ValueError:
                await ctx.sendmarkdown('> Prefix unknown.')
            else:
                await self.cfg.save()
                await ctx.sendmarkdown(f'# \'{prefix}\' has been unregistered!')

    def _parserole(self, role):
        if not role:
            return 'Owner only'
        else:
            return role

    @commands.command(aliases=['perms', 'node'])
    async def permissions(self, ctx, *, command):
        """Show information on the permission node of a given command."""

        _command = self.bot.get_command(command)

        if _command is None:
            await ctx.sendmarkdown(f'< Unknown command >')
            return

        cog_name = _command.cog.qualified_name

        out = [f'# Permission Info for: {command}\n']

        try:
            cog_node = self.cfg['nodes'][cog_name]

            for _check in _command.checks:
                if _check.__name__ == '_node_check':
                    level = _check.__closure__[0].cell_contents
                    out.append(f'Permission Level: {level.name}')
                    match level:
                        case PermissionLevel.COMMAND:
                            node = _command.qualified_name
                            role = cog_node[node]
                            out.append(f'Relevant Node: {cog_name}:{node}')
                            break
                        case PermissionLevel.GROUP:
                            node = _command.full_parent_name
                            role = cog_node[node]
                            out.append(f'Relevant Node: {cog_name}:{node}')
                            break
                        case PermissionLevel.COG:
                            node = '__core__'
                            role = cog_node[node]
                            out.append(f'Relevant Node: {cog_name}')
                            break
                        case PermissionLevel.GLOBAL:
                            role = self.cfg['nodes']['__core__']
                            break
            else:
                out.append('> No associated permission node')
                out.append('# Command is unrestricted, hurray!')
                await ctx.sendmarkdown('\n'.join(out))
                return
        except KeyError:
            role = 'owner_only'
            out.append(f'> Required minimum Role: ~~[REDACTED]~~')
        else:
            if role is None:
                role = 'owner_only'
                out.append(f'> Required minimum Role: ~~[REDACTED]~~')
            else:
                out.append(f'Required minimum Role: {role}')

        await ctx.sendmarkdown('\n'.join(out))

        is_owner = await self.bot.is_owner(ctx.author)
        if not is_owner:
            return

        if not self.cfg['hierarchy']:
            await ctx.sendmarkdown('< No hierarchy set up! Cannot edit node! >')
            return

        options = [
            discord.SelectOption(label=role_name) for role_name in self.cfg['hierarchy']
        ]
        options.extend(
            [
                discord.SelectOption(label='owner_only'),
                discord.SelectOption(label='@everyone'),
            ]
        )

        view = SelectionView(ctx, options, placeholder=role, timeout=120)

        view.msg = await ctx.sendmarkdown('# Change required minimum role: ', view=view)

        await view.wait()
        view.clear_items()

        if selected := view.values:
            if selected == 'owner_only':
                new_role = None
            else:
                new_role = selected[0]

            if level is PermissionLevel.GLOBAL:
                self.cfg['nodes']['__core__'] = new_role
            else:
                cog_node[node] = new_role

            await self.cfg.save()
            log.info(f'Required minimum Role changed to \'{selected[0]}\'')
            await view.msg.edit(
                content=f'```md\n# Required minimum Role changed to \'{selected[0]}\'!\n```',
                view=view,
            )
        else:
            await view.msg.edit(
                content='```md\n> Permissions unchanged\n```',
                view=view,
            )

    @commands.group(invoke_without_command=True, hidden=True)
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
        cogcfgflip = Flipbook(
            ctx, cogcfgentries, entries_per_page=12, title='Cog-specific Configurations'
        )
        await cogcfgflip.flip()

    @cogcfg.command(hidden=True, name='edit')
    @commands.is_owner()
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
    async def debughook(self, ctx, hookurl: str = None):
        """Returns and/or changes webhook url used for debugging purposes."""

        if 'hook' in self.cfg and self.cfg['hook'] is not None:
            await ctx.sendmarkdown(f'> Current debug webhook:\n> {self.cfg["hook"]}')
        if hookurl:
            self.cfg['hook'] = hookurl
            await self.cfg.save()
            log.info('Changed debug webhook url.')
            await ctx.sendmarkdown(f'> Set debug webhook to:\n> {hookurl}')


async def setup(bot):
    await bot.add_cog(Admin(bot))
