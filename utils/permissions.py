from discord.ext import commands
from discord.utils import find


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
