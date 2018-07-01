from discord.utils import find
from discord.ext import commands
import random
import re


async def node_check(ctx, node):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if node not in ctx.bot.cfg['nodes']:
        return False

    channels = ctx.bot.cfg['nodes'][node]['channels']
    if channels:
        if ctx.channel.id not in channels:
            return False

    roleName = ctx.bot.cfg['nodes'][node]['role']
    if roleName:
        minRole = find(lambda r: r.name == roleName, ctx.guild.roles)
        return ctx.author.top_role >= minRole
    else:
        return True


def permissionNode(node):
    async def predicate(ctx):
        return await node_check(ctx, node)
    return commands.check(predicate)


async def sendMarkdown(ctx, msg):
    return await ctx.send(f'```markdown\n{msg}\n```')


async def sendReply(ctx, msg):
    return await ctx.send(f"{random.choice(ctx.bot.keywords['replies'])}\n{msg}")


async def sendReply_codeblocked(ctx, msg, encoding=None):
    if encoding is None:
        mesg = f'\n```markdown\n{msg}\n```'
    else:
        mesg = f'\n```{encoding}\n{msg}\n```'
    return await ctx.send(f"{random.choice(ctx.bot.keywords['replies'])}" + mesg)


async def sendEmbed(ctx, emb):
    return await ctx.send(f"{random.choice(ctx.bot.keywords['replies'])}", embed=emb)


async def promptInput(ctx, prompt: str, timeout: int=120):
    """Prompt for text input.

    Returns a tuple of acquired input
    and reply message.
    """
    def check(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    await sendMarkdown(ctx, prompt)
    r = await ctx.bot.wait_for('message', check=check, timeout=timeout)
    return (r.content, r)


async def promptConfirm(ctx, prompt: str, timeout: int=120):
    """Prompt for confirmation.

    Returns a tuple of acquired confirmation
    and reply message.
    """
    def check(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    await sendMarkdown(ctx, prompt)
    r = await ctx.bot.wait_for('message', check=check, timeout=timeout)
    if re.match('^(y|yes)', r.content, flags=re.I):
        return (True, r)
    else:
        return (False, r)
