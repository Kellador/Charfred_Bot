#!/usr/bin/env python

import discord
from discord.ext import commands
from ..utils.discoutils import has_permission, sendEmbed
from ..utils.mcuser import MCUser, mojException


class stalkCmds:
    def __init__(self, bot):
        self.bot = bot
        self.stalkdict = bot.stalkdict

    @commands.command(aliases=['backgroundcheck', 'check', 'creep'])
    @has_permission('stalk')
    async def stalk(self, ctx, lookupName: str):
        print(f'Stalking {lookupName}...')
        self.stalkdict._purge()
        if lookupName in self.stalkdict:
            mcU = self.stalkdict.get(lookupName)
            print(f'Retrieved {lookupName} from cache.')
        else:
            mcU = MCUser(lookupName)
            try:
                await mcU._init(self.bot.session)
            except mojException as e:
                print(mojException.message)
                reportCard = discord.Embed(
                    title="ERROR",
                    type="rich",
                    colour=discord.Colour.dark_red()
                )
                await sendEmbed(ctx, reportCard)
            else:
                reportCard = discord.Embed(
                    title="__Subject: " + mcU.name + "__",
                    url='http://mcbouncer.com/u/' + mcU.uuid,
                    type='rich',
                    color=0x0080c0
                )
                reportCard.set_author(
                    name="Classified Report",
                    url='https://google.com/search?q=minecraft%20' +
                    mcU.name,
                    icon_url='https://crafatar.com/avatars/' +
                    mcU.uuid
                )
                reportCard.set_thumbnail(
                    url='https://crafatar.com/renders/head/' +
                    mcU.uuid + '?overlay'
                )
                reportCard.add_field(
                    name="Current Name:",
                    value="```\n" + mcU.name + "\n```"
                )
                reportCard.add_field(
                    name="UUID:",
                    value="```\n" + mcU.uuid + "\n```"
                )
                if mcU.demo:
                    reportCard.add_field(name="__**DEMO ACCOUNT**__")
                if mcU.legacy:
                    reportCard.add_field(name="*Legacy*")
                if mcU.nameHistory is not None:
                    pastNames = ', '.join(mcU.nameHistory)
                    reportCard.add_field(name="Past names:",
                                         value=pastNames)
                reportCard.set_footer(text="Report compiled by Agent Charfred")
                await sendEmbed(ctx, reportCard)


def setup(bot):
    bot.add_cog(stalkCmds(bot))
