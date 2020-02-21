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
            hierarchy = set(ctx.bot.cfg['hierarchy'])
            roles = [r for r in ctx.author.roles if r.name in hierarchy]
            if roles:
                return roles[-1] >= minRole
        return False


def permission_node(node):
    async def predicate(ctx):
        return await node_check(ctx, node)
    return commands.check(predicate)


formatpat = re.compile('^[`]{3}(?P<format>\w+|\s)')


def _splitup(msg, codeblocked=False):
    msg = msg.splitlines(keepends=True)
    if codeblocked:
        s = formatpat.search(msg)
        if s.group('format'):
            front = f'```{s.group("format")}\n'
        back = '\n```'
    else:
        front = ''
        back = ''
    msg.reverse()
    msgs = []
    part = front
    while True:
        if len(msg) > 0:
            next = msg.pop()
        else:
            if part:
                part += back
                msgs.append(part)
            break

        if (len(part) + len(next)) < 1990:
            part += next
        else:
            part += back
            msgs.append(part)
            part = front + next

    return msgs


async def send(ctx, msg=None, deletable=True, embed=None, codeblocked=False):
    """Helper function to send all sorts of things!

    Messages are automatically split into multiple messages if they're too long,
    and if the codeblocked parameter is True codeblock formatting is
    preserved when such a split occurs.

    Returns the message object for the sent message,
    if a split was performed only the last sent message is returned.
    """
    if (msg is None) or (len(msg) <= 2000):
        outmsg = await ctx.send(content=msg, embed=embed)
        if deletable:
            try:
                ctx.bot.cmd_map[ctx.message.id].output.append(outmsg)
            except KeyError:
                pass
            except AttributeError:
                pass
        return outmsg
    else:
        msgs = _splitup(msg, codeblocked)
        for msg in msgs:
            outmsg = await send(ctx, msg, deletable, codeblocked=codeblocked)
        return outmsg


async def sendmarkdown(ctx, msg, deletable=True):
    """Helper function that wraps a given message in markdown codeblocks
    and sends if off.

    Because laziness is the key to great success!
    """
    return await send(ctx, f'```markdown\n{msg}\n```', deletable=deletable, codeblocked=True)


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
