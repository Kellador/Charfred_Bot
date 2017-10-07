#!/usr/bin/env python

from discord.ext import commands
import re
from ..utils.discoutils import has_perms, sendReply, valid_servertarget
from ..utils.executors import exec_cmd
from .. import configs as cfg


class crashReporter:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['report', 'crashreports'], ignore_extra=False)
    @has_perms()
    @valid_servertarget()
    async def crashreport(self, ctx, server: str):
        # TODO: Replace this with the implementation in spiffyManagement!
        if ctx.args.len() == 2 and re.match('^\d$', ctx.args[1]):
            report = await exec_cmd(
                ctx,
                cfg.commands['crashreport']['Script'],
                'crashreport',
                server, ctx.args[1]
            )
        else:
            report = await exec_cmd(
                ctx,
                cfg.commands['crashreport']['Script'],
                'crashreport',
                server
            )
        params = {
            'api_dev_key': cfg.pastebinToken,
            'api_option': 'paste',
            'api_paste_code': report,
            'api_user_key': self.bot.pasteKey,
            'api_paste_private': '2',
            'api_paste_expire_date': '10M'
        }
        async with self.bot.session as cs:
            async with cs.get('https://pastebin.com/api/api_post.php',
                              params=params) as resp:
                pasteLink = await resp.text()
                print(f'Generated pastebin link: {pasteLink}')
        await sendReply(ctx, pasteLink)


def setup(bot):
    bot.add_cog(crashReporter(bot))
