from discord.ext import commands
import traceback
import logging
import random

log = logging.getLogger('charfred')


class ErrorHandler:
    def __init__(self, bot):
        self.bot = bot
        self.keywords = bot.keywords
        self.session = bot.session
        self.cfg = bot.cfg

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            await ctx.send('Sorry chap, that command\'s disabled!')
            log.warning(f'DisabledCommand: {ctx.command.qualified_name}')

        elif isinstance(error, commands.NotOwner):
            await ctx.send('You\'re not the boss of me, sir!')
            log.warning(f'NotOwner: {ctx.author.name}: {ctx.command.qualified_name}')

        elif isinstance(error, commands.CheckFailure):
            await ctx.send(random.choice(self.keywords['errormsgs']))
            log.warning(f'CheckFailure: {ctx.author.name}: {ctx.command.qualified_name} in {ctx.channel.name}!')

        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(random.choice(self.keywords['nacks']))
            log.warning(f'CommandNotFound: {ctx.invoked_with}')

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You\'re missing some arguments there, mate!')
            log.warning(f'MissingRequiredArgument: {ctx.command.qualified_name}')

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send('Stop it, you\'re making me blush...')
            log.warning(f'NoPrivateMessage: {ctx.author.name}: {ctx.command.qualified_name}')

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(random.choice(self.keywords['errormsgs']))
            log.warning(f'MissingPermissions: {ctx.author.name}: {ctx.command.qualified_name}')

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('I am not allowed to do that, sir, it is known!')
            log.warning(f'BotMissingPermissions: {ctx.command.qualified_name}')

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send('Sorry lass, that command\'s on cooldown!\n'
                           f'Try again in {error.retry_after} seconds.')
            log.warning(f'CommandOnCooldown: {ctx.command.qualified_name}')

        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(random.choice(self.keywords['nacks']))

            hook_url = self.cfg['hook']
            if hook_url:
                hook_this = {
                    "embeds": [
                        {
                            "title": f"Exception during Command: {ctx.command.qualified_name}",
                            "description": f"```py\n{traceback.format_exc(error.original)}\n```",
                            "color": 15102720
                        }
                    ]
                }

                async with self.session.post(hook_url, json=hook_this) as r:
                    await r.read()

            log.error(f'{ctx.command.qualified_name}:')
            log.error(f'{error.original.__class__.__name__}: {error.original}')
            traceback.print_tb(error.original.__traceback__)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
