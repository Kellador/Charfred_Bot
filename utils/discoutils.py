import discord
from discord.ext import commands
import random
import re
import functools


async def node_check(ctx, node):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    channels = ctx.bot.cfg['nodes'][node]['channels']
    if channels:
        if ctx.channel.id not in channels:
            return False

    roles = ctx.bot.cfg['nodes'][node]['roles']
    getter = functools.partial(discord.utils.get, ctx.author.roles)
    return any(getter(name=roleName) is not None for roleName in roles)


def permissionNode(node):
    async def predicate(ctx):
        return await node_check(ctx, node)
    return commands.check(predicate)


async def sendReply(ctx, msg):
    await ctx.send(f"{random.choice(ctx.bot.keywords['replies'])}\n{msg}")


async def sendReply_codeblocked(ctx, msg, encoding=None):
    if encoding is None:
        mesg = f'\n```markdown\n{msg}\n```'
    else:
        mesg = f'\n```{encoding}\n{msg}\n```'
    await ctx.send(f"{random.choice(ctx.bot.keywords['replies'])}" + mesg)  # fix this!


async def sendEmbed(ctx, emb):
    await ctx.send(f"{random.choice(ctx.bot.keywords['replies'])}", embed=emb)  # fix this too!


async def promptInput(ctx, prompt: str):
    """Prompt for text input."""
    def check(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    await ctx.send(prompt)
    r = await ctx.bot.wait_for('message', check=check, timeout=120)
    return r.content


async def promptConfirm(ctx, prompt: str):
    """Prompt for confirmation."""
    def check(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    await ctx.send(prompt)
    r = await ctx.bot.wait_for('message', check=check, timeout=120)
    if re.match('^(y|yes)', r.content, flags=re.I):
        return True
    else:
        return False
