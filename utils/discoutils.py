import re
from asyncio import TimeoutError
from discord.utils import find
from discord.ext import commands


async def node_check(ctx, node):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    try:
        if not ctx.bot.cfg['nodes'][node]:
            return False
    except KeyError:
        return False

    roleName = ctx.bot.cfg['nodes'][node]
    if roleName == '@everyone':
        return True
    else:
        minRole = find(lambda r: r.name == roleName, ctx.guild.roles)
        if minRole:
            return ctx.author.top_role >= minRole
        return False


def permission_node(node):
    async def predicate(ctx):
        return await node_check(ctx, node)
    return commands.check(predicate)


async def send(ctx, msg=None, deletable=True, embed=None):
    outmsg = await ctx.send(content=msg, embed=embed)
    if deletable:
        try:
            ctx.bot.cmd_map[ctx.message.id].output.append(outmsg)
        except KeyError:
            pass
        except AttributeError:
            pass
    return outmsg


async def sendmarkdown(ctx, msg, deletable=True):
    if deletable:
        return await send(ctx, f'```markdown\n{msg}\n```')
    else:
        return await ctx.send(f'```markdown\n{msg}\n```')


def _splitup(msg, markdown=False):
    msg = msg.splitlines(keepends=True)
    msg.reverse()
    msgs = []
    part = ''
    while True:
        if len(msg) > 0:
            next = msg.pop()
        else:
            if part:
                if markdown:
                    part += '\n```'
                msgs.append(part)
            break
        if (len(part) + len(next)) < 1990:
            part += next
        else:
            if markdown:
                part += '```'
            msgs.append(part)
            if markdown:
                part = '```\n' + next
            else:
                part = next
    return msgs


async def sendlong(ctx, msg, deletable=True, markdown=False):
    if len(msg) <= 2000:
        if markdown:
            await sendmarkdown(ctx, msg, deletable)
        else:
            await send(ctx, msg, deletable)
    else:
        msgs = _splitup(msg, markdown)
        if markdown:
            for msg in msgs:
                await sendmarkdown(ctx, msg, deletable)
        else:
            for msg in msgs:
                await send(ctx, msg, deletable)


async def promptinput(ctx, prompt: str, timeout: int=120, deletable=True):
    """Prompt for text input.

    Returns a tuple of acquired input,
    reply message, and boolean indicating prompt timeout.
    """
    def check(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    await sendmarkdown(ctx, prompt, deletable)
    try:
        r = await ctx.bot.wait_for('message', check=check, timeout=timeout)
    except TimeoutError:
        await sendmarkdown(ctx, '> Prompt timed out!', deletable)
        return (None, None, True)
    else:
        return (r.content, r, False)


async def promptconfirm(ctx, prompt: str, timeout: int=120, deletable=True):
    """Prompt for confirmation.

    Returns a triple of acquired confirmation,
    reply message, and boolean indicating prompt timeout.
    """
    def check(m):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    await sendmarkdown(ctx, prompt, deletable)
    try:
        r = await ctx.bot.wait_for('message', check=check, timeout=timeout)
    except TimeoutError:
        await sendmarkdown(ctx, '> Prompt timed out!', deletable)
        return (None, None, True)
    else:
        if re.match('^(y|yes)', r.content, flags=re.I):
            return (True, r, False)
        else:
            return (False, r, False)
