import logging
import pprint
from collections import namedtuple
from discord.errors import Forbidden, NotFound
from discord.ext import commands
from utils.discoutils import sendMarkdown
from utils.sizeddict import SizedDict

log = logging.getLogger('charfred')

Command = namedtuple('Command', 'msg output')


class CommandHistorian:
    def __init__(self, bot):
        self.bot = bot
        self.botCfg = bot.cfg
        self.pprinter = pprint.PrettyPrinter()
        self.cmd_map = SizedDict()
        if not hasattr(bot, 'cmd_map'):
            bot.cmd_map = self.cmd_map

    async def on_command(self, ctx):
        self.cmd_map[ctx.message.id] = Command(
            msg=ctx.message,
            output=[]
        )

    @commands.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def cmdmap(self, ctx):
        """Command Map commands.

        Without a subcommand, this returns a crude list of
        the current command map state.
        """

        log.info('Showing cmd_map.')
        rep = self.pprinter.pformat(self.cmd_map)
        await sendMarkdown(ctx, rep)

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
            await sendMarkdown(ctx, 'Command map cleared, new maximum size set '
                               f'to {max_size}!')
        else:
            log.warning('cmd_map clear with insufficient max_size!')
            await sendMarkdown(ctx, '< Insufficient maximum size, you can\'t '
                               'even store a single command in there! >')

    @commands.group(aliases=['cmdhistory'])
    async def history(self, ctx):
        """Command-history commands."""

        if ctx.invoked_subcommand is None:
            pass

    @commands.command(name='!!', aliases=['again'])
    async def _repeat(self, ctx):
        """Reinvokes the last command issued by the user of this command.

        Given that the last command has not expired and been removed from
        the command history yet.
        """

        lastcmd = self.cmd_map.find(lambda c: c.msg.author.id == ctx.author.id)
        if not lastcmd:
            log.info(f'No recent command found for {ctx.author.name}.')
            await sendMarkdown(ctx, '> Could not find any recent command of yours,'
                               ' sorry.')
            return
        await sendMarkdown(ctx, f'# Last command found!')

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
                await self.bot.on_message(after)
                del self.cmd_map[before.id]


def setup(bot):
    bot.add_cog(CommandHistorian(bot))
