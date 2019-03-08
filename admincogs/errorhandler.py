from discord.ext import commands
import traceback
import logging
import random
from utils.discoutils import sendMarkdown

log = logging.getLogger('charfred')


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keywords = bot.keywords
        self.session = bot.session
        self.cfg = bot.cfg

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await sendMarkdown(ctx, '> Sorry chap, that command\'s disabled!')
            log.warning(f'DisabledCommand: {ctx.command.qualified_name}')

        elif isinstance(error, commands.NotOwner):
            await sendMarkdown(ctx, '< You\'re not the boss of me, sir! >')
            log.warning(f'NotOwner: {ctx.author.name}: {ctx.command.qualified_name}')

        elif isinstance(error, commands.CheckFailure):
            await sendMarkdown(ctx, '< ' + random.choice(self.keywords['errormsgs']) + ' >')
            log.warning(f'CheckFailure: {ctx.author.name}: {ctx.command.qualified_name} in {ctx.channel.name}!')

        elif isinstance(error, commands.CommandNotFound):
            await sendMarkdown(ctx, '> ' + random.choice(self.keywords['nacks']))
            log.warning(f'CommandNotFound: {ctx.invoked_with}')

        elif isinstance(error, commands.MissingRequiredArgument):
            await sendMarkdown(ctx, '> You\'re missing some arguments there, mate!')
            log.warning(f'MissingRequiredArgument: {ctx.command.qualified_name}')

        elif isinstance(error, commands.NoPrivateMessage):
            await sendMarkdown(ctx, '# Stop it, you\'re making me blush...')
            log.warning(f'NoPrivateMessage: {ctx.author.name}: {ctx.command.qualified_name}')

        elif isinstance(error, commands.MissingPermissions):
            await sendMarkdown(ctx, '< ' + random.choice(self.keywords['errormsgs']) + ' >')
            log.warning(f'MissingPermissions: {ctx.author.name}: {ctx.command.qualified_name}')

        elif isinstance(error, commands.BotMissingPermissions):
            await sendMarkdown(ctx, '< I am not allowed to do that, sir, it is known! >')
            log.warning(f'BotMissingPermissions: {ctx.command.qualified_name}')

        elif isinstance(error, commands.CommandOnCooldown):
            await sendMarkdown(ctx, '> Sorry lass, that command\'s on cooldown!\n'
                               f'> Try again in {error.retry_after} seconds.')
            log.warning(f'CommandOnCooldown: {ctx.command.qualified_name}')

        elif isinstance(error, commands.CommandInvokeError):
            await sendMarkdown(ctx, '< ' + random.choice(self.keywords['nacks']) + ' >')

            hook_url = self.cfg['hook']
            if hook_url:
                hook_this = {
                    "embeds": [
                        {
                            "title": f"Exception during Command: {ctx.command.qualified_name}",
                            "description": f"```py\n{error}:\n{traceback.format_tb(error.original.__traceback__)}\n```",
                            "color": 15102720
                        }
                    ]
                }
                await self.session.post(hook_url, json=hook_this)

            log.error(f'{ctx.command.qualified_name}:')
            log.error(f'{error.original.__class__.__name__}: {error.original}')
            traceback.print_tb(error.original.__traceback__)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
