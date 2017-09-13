#!/usr/bin/env python

from discord.ext import commands
import aiohttp
import subprocess
from .utils import rolecall


class Crasher:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['crash', 'report', 'crashreports'])
    @rolecall.is_staff()
    async def crashreport(ctx, message: str):
