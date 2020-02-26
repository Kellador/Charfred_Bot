import logging
import pprint
import asyncio
import discord
from copy import copy
from collections import namedtuple
from discord.errors import Forbidden, NotFound
from discord.ext import commands
from utils import SizedDict

log = logging.getLogger('charfred')

Command = namedtuple('Command', 'msg output')


class CommandHistorian(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.botCfg = bot.cfg
        self.loop = bot.loop
        self.lock = asyncio.Lock()
        self.pprinter = pprint.PrettyPrinter()
        if not hasattr(bot, 'cmd_map'):
            self.cmd_map = SizedDict()
            bot.cmd_map = self.cmd_map
        else:
            self.cmd_map = bot.cmd_map

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Saves message attached to command context to the command map,
        and optionally logs command to users command history file.
        """

        self.cmd_map[ctx.message.id] = Command(
            msg=ctx.message,
            output=[]
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Deletes command output if original invokation
        message is deleted.

        Will only work if the command is still in the
        cmd_map and hasn\'t expired yet!
        """

        if message.id in self.cmd_map:
            log.info('Deleting previous command output!')
            try:
                await message.channel.delete_messages(self.cmd_map[message.id].output)
            except KeyError:
                log.error('Deletion of previous command output failed!')
            except Forbidden:
                log.error('No Permission!')
            except NotFound:
                log.warning('Some messages not found for deletion!')
            else:
                del self.cmd_map[message.id]

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Reinvokes a command if it has been edited,
        and deletes previous command output.

        Will only work if the command is still in the
        cmd_map and hasn\'t expired yet!
        """

        if before.content == after.content:
            return

        if before.id in self.cmd_map:
            log.info('Deleting previous command output!')
            try:
                await before.channel.delete_messages(self.cmd_map[before.id].output)
            except KeyError:
                log.error('Deletion of previous command output failed!')
            except Forbidden:
                log.error('No Permission!')
            except NotFound:
                log.warning('Some messages not found for deletion!')
            else:
                log.info(f'Reinvoking: {before.content} -> {after.content}')
                del self.cmd_map[before.id]
                await self.bot.on_message(after)

    def _removefrommap(self, ctx):
        log.info('Command removed from command map!')
        try:
            del self.cmd_map[ctx.message.id]
        except KeyError:
            pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            self._removefrommap(ctx)
        elif isinstance(error, commands.CheckFailure):
            self._removefrommap(ctx)
        elif isinstance(error, commands.MissingPermissions):
            self._removefrommap(ctx)
        elif isinstance(error, commands.CommandNotFound):
            if ctx.message.id not in self.cmd_map:
                self.cmd_map[ctx.message.id] = Command(
                    msg=ctx.message,
                    output=[]
                )

    @commands.command(aliases=['!!'])
    async def last(self, ctx):
        """Reinvokes the last command executed by the user.

        Specifically the last command invoked in the channel that 'last'
        was invoked in.
        """

        lastcmd = self.cmd_map.find(lambda cmd: (cmd.msg.channel.id == ctx.channel.id) and
                                    (cmd.msg.author.id == ctx.author.id))
        if lastcmd:
            log.info('Last command found, reinvoking...')
            await self.bot.on_message(lastcmd.msg)
        else:
            log.info('No last command found!')
            await ctx.sendmarkdown('> No recent command found in current channel!')

    async def rejig_ctx(self, ctx, content=None, author=None, channel=None):
        """Create a copy of a Context with some variables changed."""

        copiedmsg = copy(ctx.message)
        if content:
            copiedmsg.content = content
        if author:
            copiedmsg.author = author
        if channel:
            copiedmsg.channel = channel

        return await ctx.bot.get_context(copiedmsg)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def su(self, ctx, user: discord.User, *, cmd: str):
        """Substitute user, like the unix command!"""

        try:
            user = ctx.guild.get_member(user.id) or user
        except AttributeError:
            pass

        rectx = await self.rejig_ctx(ctx, content=f'{ctx.prefix}{cmd}', author=user)
        if rectx.command:
            await rectx.command.invoke(rectx)
        else:
            await ctx.sendmarkdown(f'No valid command for "{rectx.invoked_with}" found!')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def cast(self, ctx, channel: discord.TextChannel, *, cmd: str):
        """Cast a command to another channel."""

        rectx = await self.rejig_ctx(ctx, content=f'{ctx.prefix}{cmd}', channel=channel)
        if rectx.command:
            await rectx.command.invoke(rectx)
        else:
            await ctx.sendmarkdown(f'No valid command for "{rectx.invoked_with}" found!')

    @commands.group(hidden=True, invoke_without_command=True)
    @commands.is_owner()
    async def cmdlogging(self, ctx):
        """Command logging commands.

        Returns whether logging is currently enabled or not,
        if no subcommand is given.
        """

        log.info('Logging is currently ' + ('active!' if self.logcmds else 'inactive!'))
        await ctx.sendmarkdown('# Logging is currently ' + ('active!' if self.logcmds else 'inactive!'))

    @cmdlogging.command(hidden=True)
    @commands.is_owner()
    async def toggle(self, ctx):
        """Toggles command logging on and off."""

        if self.logcmds:
            self.logcmds = False
        else:
            self.logcmds = True
        log.info('Toggled command logging ' + ('off!' if self.logcmds else 'on!'))
        await ctx.sendmarkdown('# Toggled command logging ' + ('off!' if self.logcmds else 'on!'))

    @commands.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def cmdmap(self, ctx):
        """Command Map commands.

        This returns a crude list of the current command map state,
        if no subcommand was given.
        """

        log.info('Showing cmd_map.')
        rep = self.pprinter.pformat(self.cmd_map)
        await ctx.sendmarkdown(rep)

    @cmdmap.command(hidden=True)
    @commands.is_owner()
    async def clear(self, ctx, max_size: int=100):
        """Clears the current command map.

        Optionally takes a number for the maximum
        size of the command map.
        """

        if max_size > 1:
            log.info(f'Clearing cmd_map, setting maximum size to: {max_size}.')
            self.cmd_map.clear()
            self.cmd_map.max_size = max_size
            await ctx.sendmarkdown('Command map cleared, new maximum size set '
                                   f'to {max_size}!')
        else:
            log.warning('cmd_map clear with insufficient max_size!')
            await ctx.sendmarkdown('< Insufficient maximum size, you can\'t '
                                   'even store a single command in there! >')


def setup(bot):
    bot.add_cog(CommandHistorian(bot))
