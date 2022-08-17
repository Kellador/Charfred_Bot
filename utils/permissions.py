from discord.ext import commands
from discord.utils import find
from enum import Enum
import logging

log = logging.getLogger('charfred.permissions')


class PermissionLevel(Enum):
    COMMAND = 1
    GROUP = 2
    COG = 3
    GLOBAL = 4


async def node_check(ctx, level: PermissionLevel):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    try:
        cog_node = ctx.bot.cfg['nodes'][ctx.command.cog.qualified_name]

        match level:
            case PermissionLevel.COMMAND:
                role = cog_node[ctx.command.qualified_name]
            case PermissionLevel.GROUP:
                role = cog_node[ctx.command.full_parent_name]
            case PermissionLevel.COG:
                role = cog_node['__core__']
            case PermissionLevel.GLOBAL:
                role = ctx.bot.cfg['nodes']['__core__']
    except KeyError as e:
        log.warning(e)
        return False

    if role is None:
        log.warning(
            f'{ctx.author.name} lacks permission to use {ctx.command.qualified_name}'
        )
        return False

    if role == '@everyone':
        return True
    else:
        minRole = find(lambda r: r.name == role, ctx.guild.roles)
        if minRole:
            hierarchy = set(ctx.bot.cfg['hierarchy'])
            roles = [r for r in ctx.author.roles if r.name in hierarchy]
            if roles:
                return roles[-1] >= minRole
        log.warning(
            f'{ctx.author.name} lacks permission to use {ctx.command.qualified_name}'
        )
        return False


def restricted(level: PermissionLevel = PermissionLevel.COMMAND):
    async def _node_check(ctx):
        return await node_check(ctx, level)

    return commands.check(_node_check)
