#!/usr/bin/env python

from discord.ext import commands
import re
from ..utils.discoutils import has_permission, sendReply, valid_servertarget
from .. import configs as cfg


class crashReporter:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['report', 'crashreports'], ignore_extra=False)
    @has_permission('crashreport')
    @valid_servertarget()
    async def crashreport(self, ctx, server: str):
        # TODO:
        # """Retrieves the last crashreport for the given server;
        # Takes a relative age parameter, 0 for the newest report,
        # 1 for the one before, etc.
        # """
        # if age is None:
        #     reportFile = sorted(
        #         glob.iglob(cfg['serverspath'] + f'/{server}/crash-reports/*'),
        #         key=os.path.getmtime,
        #         reverse=True
        #     )[0]
        # else:
        #     reportFile = sorted(
        #         glob.iglob(cfg['serverspath'] + f'/{server}/crash-reports/*'),
        #         key=os.path.getmtime,
        #         reverse=True
        #     )[age]
        # TODO: Work out a python solution for this.
        # proc = await asyncio.create_subprocess_exec(
        #     'awk',
        #     '/^Time: /{e=1}/^-- Head/{e=1}/^-- Block/{e=1}/^-- Affected/{e=1}/^-- System/{e=0}/^A detailed/{e=0}{if(e==1){print}}',
        #     reportFile
        #     stdout=asyncio.subprocess.PIPE,
        #     stderr=asyncio.subprocess.PIPE
        # )
        # log.info(f'Getting report for {server}.')
        # stdout, stderr = await proc.communicate()
        # if proc.returncode == 0:
        #     log.info(f'Report retrieved successfully.')
        # else:
        #     log.warning('Failed to retrieve report!')
        # return stdout.decode().strip()
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
