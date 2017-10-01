#!/usr/bin/env python

import asyncio
from .discoutils import sendReply_codeblocked


async def exec_cmd(ctx, *args):
    """Runs a given (shell) command and returns the output"""
    async with ctx.typing():
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        print('Executing:', args)
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            print('Finished:', args)
        else:
            print('Failed:', args)
        return stdout.decode().strip()


async def exec_cmd_reply(ctx, *args):
    """Runs a given (shell) command and sends the output
    as a codeblocked message to the appropriate commandchannel"""
    async with ctx.typing():
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE
        )
        print('Executing:', args)
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            print('Finished:', args)
        else:
            print('Failed:', args)
        msg = stdout.decode().strip()
        await sendReply_codeblocked(ctx, msg)


# === This doesn't really work all that well because it will block         ===
# === Better to just wait for the entire output and send typing meanwhile  ===
# async def exec_cmd_staggeredReply(ctx, *args):
#     if is_cmdChannel(ctx):
#         ch = ctx.channel
#     else:
#         ch = get_cmdCh(ctx)
#     proc = await asyncio.create_subprocess_exec(
#         *args, stdout=asyncio.subprocess.PIPE
#     )
#     print('Executing:', args)
#     out = ['```']
#     # TODO
#     await ctx.send(f'{random.choice(cfg.deposits)}\n{msg.channel.mention}')
