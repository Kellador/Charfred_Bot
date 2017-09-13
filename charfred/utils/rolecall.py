#!/usr/bin/env python

from discord.ext import commands
import configs as cfg


async def roleCall(ctx, requiredRole):
    for role in ctx.author.roles:
        if role.name in cfg.roles:
            if cfg.roles.index(role.name) >= cfg.roles.index(requiredRole):
                return True
    return False


def is_owner():
    async def predi(ctx):
        return await ctx.bot.is_owner(ctx.author)
    return commands.check(predi)


def is_staff():
    async def predi(ctx):
        return await roleCall(ctx, 'Staff')
    return commands.check(predi)


def is_moderator():
    async def predi(ctx):
        return await roleCall(ctx, 'Moderator')
    return commands.check(predi)


def is_helper():
    async def predi(ctx):
        return await roleCall(ctx, 'Helper')
    return commands.check(predi)
