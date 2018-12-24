import logging
import pprint
from discord.errors import Forbidden, NotFound
from discord.ext import commands
from utils.discoutils import sendMarkdown
from utils.simplettldict import SimpleTTLDict

log = logging.getLogger('charfred')


class CmdHistorian:
    def __init__(self, bot):
        self.bot = bot
        self.cmd_map = bot.cmd_map
        self.botCfg = bot.cfg
        self.pprinter = pprint.PrettyPrinter()

    @commands.group(invoke_without_command=True, hidden=True)
    @commands.is_owner()
    async def cmdmap(self, ctx):
        """Command Map operations.

        Without a subcommand, this returns a crude list of
        the current command map state.
        """

        log.info('Showing cmd_map.')
        rep = self.pprinter.pformat(self.cmd_map)
        await sendMarkdown(ctx, rep)

    @cmdmap.command(hidden=True)
    @commands.is_owner()
    async def clear(self, ctx):
        """Clears the current Command Map."""

        log.info('Clearing cmd_map.')
        self.cmd_map = SimpleTTLDict()

    async def on_message_delete(self, message):
        """Deletes command output if original invokation
        message is deleted.

        Will only work if the command is still in the
        cmd_map and hasn\'t expired yet!
        """

        if message.id in self.cmd_map:
            log.info('Deleting previous command output!')
            try:
                await message.channel.delete_messages(self.cmd_map[message.id][0])
            except KeyError:
                log.error('Deletion of previous command output failed!')
            except Forbidden:
                log.error('No Permission!')
            except NotFound:
                log.warning('Some messages not found for deletion!')

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
                await before.channel.delete_messages(self.cmd_map[before.id][0])
            except KeyError:
                log.error('Deletion of previous command output failed!')
            except Forbidden:
                log.error('No Permission!')
            except NotFound:
                log.warning('Some messages not found for deletion!')
            else:
                log.info(f'Reinvoking: {before.content} -> {after.content}')
                await self.bot.on_message(after)


def setup(bot):
    if not hasattr(bot, 'cmd_map'):
        bot.cmd_map = SimpleTTLDict()
    bot.add_cog(CmdHistorian(bot))
