import logging
import asyncio
import discord

log = logging.getLogger('charfred')


class Flipbook:
    """Allows splitting list entries into
    pages, that can be flipped through via
    reactions.

    Heavily based on RoboDanny's Paginator."""
    def __init__(self, ctx, entries, entries_per_page=16, title=None, color=None,
                 close_on_exit=False):
        self.bot = ctx.bot
        self.ctx = ctx
        self.helping = False
        self.title = title
        self.entries = entries
        self.entries_per_page = entries_per_page
        self.pages, odds = divmod(len(self.entries), self.entries_per_page)
        if odds:
            self.pages += 1
        if self.pages > 1:
            self.flipable = True
        else:
            self.flipable = False
        if color is None:
            self.embed = discord.Embed(color=discord.Color.orange())
        else:
            self.embed = discord.Embed(color=color)
        self.close_on_exit = close_on_exit
        self.bttns = [
            ('👈', self.flip_back),
            ('🖕', self.flip_off),
            ('❔', self.info),
            ('👉', self.flip_forward)
        ]

    def flip_entries(self, page):
        start = page * self.entries_per_page
        return self.entries[start:start + self.entries_per_page]

    async def draw_page(self, page, first=False):
        if page < 0 or page > (self.pages - 1):
            return

        self.current_page = page
        entries = self.flip_entries(page)
        content = []
        for e in entries:
            content.append(e)

        if self.title:
            self.embed.title = self.title

        if self.pages > 1:
            self.embed.set_footer(text=f'Page {page} of {self.pages - 1}')
        else:
            self.embed.set_footer(text=u'Got it all on one page! ╭( ･ㅂ･)و')

        self.embed.description = '\n'.join(content)

        if first:
            self.msg = await self.ctx.send(embed=self.embed)

            if self.flipable:
                for (bttn, _) in self.bttns:
                    await self.msg.add_reaction(bttn)
        else:
            await self.msg.edit(embed=self.embed)

    async def flip_back(self):
        await self.draw_page(self.current_page - 1)

    async def flip_forward(self):
        await self.draw_page(self.current_page + 1)

    async def flip_off(self):
        self.flipable = False
        if self.close_on_exit:
            await self.msg.edit(embed=None,
                                content='```markdown\n> FlipBook closed!\n```')
        await self.msg.clear_reactions()

    async def info(self):
        if self.helping:
            self.helping = False
            await self.draw_page(self.current_page)
        else:
            self.helping = True
            content = [
                'Flip through by reacting to this embed!',
                ' ',
                'Flip backwards: 👈',
                'Flip forwards:  👉',
                'Flip Charfred off: 🖕 (closes Flipbook)',
                'Toggle this help: ❔'
            ]

            infoEmbed = discord.Embed(color=discord.Color.blurple())
            infoEmbed.title = 'Charfred Flipbook Instructions:'
            infoEmbed.description = '\n'.join(content)
            await self.msg.clear_reactions()
            await self.msg.edit(embed=infoEmbed)
            await self.msg.add_reaction('❔')
            await self.msg.add_reaction('🖕')

    async def flip(self):
        await self.draw_page(0, first=True)

        def check(reaction, user):
            if reaction.message.id != self.msg.id:
                return False

            if user.id != self.ctx.author.id:
                return False

            for (bttn, func) in self.bttns:
                if str(reaction.emoji) == bttn:
                    self.action = func
                    return True
            return False

        while self.flipable:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=120, check=check)
            except asyncio.TimeoutError:
                self.flipable = False
                self.action = self.flip_off
                try:
                    await self.msg.clear_reactions()
                except:
                    pass
            else:
                try:
                    await self.msg.remove_reaction(reaction, user)
                except:
                    pass
            await self.action()


class EmbedFlipbook(Flipbook):
    """Flipbook, but for flipping through
    a list of embeds!"""
    async def draw_page(self, page, first=False):
        if page < 0 or page > (self.pages - 1):
            return

        self.current_page = page
        self.embed = self.entries[page]

        if self.title:
            self.embed.title = self.title

        if self.pages > 1:
            self.embed.set_footer(text=f'Page {page} of {self.pages - 1}')
        else:
            self.embed.set_footer(text=u'Got it all on one page! ╭( ･ㅂ･)و\n'
                                  'Wait... why make a Flipbook for just one embed?')

        if first:
            self.msg = await self.ctx.send(embed=self.embed)

            for (bttn, _) in self.bttns:
                await self.msg.add_reaction(bttn)
        else:
            await self.msg.edit(embed=self.embed)
