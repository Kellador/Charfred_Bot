#!/usr/bin/env python

from discord.ext import commands
import random
import re
from .. import configs as cfg
from .. import keywords


targetsPattern = re.compile(
    ('|'.join(map(re.escape, list(cfg.servers.keys())))),
    re.IGNORECASE
)


async def roleCall(ctx):
    print(ctx.command.name)
    requiredRole = cfg.commands[ctx.command.name]['MinRank']
    for role in ctx.author.roles:
        if role.name in cfg.roles:
            if cfg.roles.index(role.name) >= cfg.roles.index(requiredRole):
                return True
    return False


def is_owner():
    async def predicate(ctx):
        return await ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)


def has_perms():
    async def predicate(ctx):
        return await roleCall(ctx)
    return commands.check(predicate)


async def targetCheck(ctx):
    if ctx.args[0] in cfg.servers.keys():
        if ctx.command.name not in cfg.servers[ctx.args[0]]:
            return True
    return False


def valid_servertarget():
    async def predicate(ctx):
        return await targetCheck(ctx)
    return commands.check(predicate)


def is_cmdChannel(ctx):
    if ctx.channel.id in cfg.commandCh.keys():
        return True
    return False


# for decorator use only
def _is_cmdChannel(ctx):
    async def predicate(ctx):
        return is_cmdChannel(ctx)
    return commands.check(predicate)


def get_cmdCh(ctx):
    cmdChID = cfg.commandCh[ctx.guild.id]
    return ctx.bot.get_channel(cmdChID)


async def sendReply(ctx, msg):
    if is_cmdChannel(ctx):
        await ctx.send(f'{random.choice(keywords.replies)}\n{msg}')
    else:
        await get_cmdCh(ctx).send(f'{random.choice(keywords.replies)}\n{msg}')
        await ctx.send(
            f'{random.choice(keywords.deposits)}\n{get_cmdCh(ctx).mention}',
            delete_after=60
        )


async def sendReply_codeblocked(ctx, msg):
    if is_cmdChannel(ctx):
        await ctx.send(
            f'{random.choice(keywords.replies)}',
            f'\n```{cfg.blockEncoding}\n{msg}\n```'
        )
    else:
        await get_cmdCh(ctx).send(
            f'{random.choice(keywords.replies)}',
            f'\n```{cfg.blockEncoding}\n{msg}\n```'
        )
        await ctx.send(
            f'{random.choice(keywords.deposits)}\n{get_cmdCh(ctx).mention}',
            delete_after=60
        )


async def sendEmbed(ctx, emb):
    if is_cmdChannel(ctx):
        await ctx.send(
            f'{random.choice(keywords.replies)}',
            embed=emb
        )
    else:
        await get_cmdCh(ctx).send(
            f'{random.choice(keywords.replies)}',
            embed=emb
        )
        await ctx.send(
            f'{random.choice(keywords.deposits)}\n{get_cmdCh(ctx).mention}',
            delete_after=60
        )
