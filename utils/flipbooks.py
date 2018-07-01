import logging
import asyncio
import discord
from itertools import chain
from utils.discoutils import promptConfirm, promptInput, sendMarkdown

log = logging.getLogger('charfred')


class Flipbook:
    """Allows splitting list entries into
    pages, that can be flipped through via
    reactions.

    Totally based on RoboDanny's Paginator."""
    def __init__(self, ctx, entries, entries_per_page=16, title=None, color=None):
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
        await self.msg.edit(embed=None,
                            content='```markdown\n> FlipBook closed!\n```')

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
                reaction, user = await self.bot.wait_for('reaction_add', timeout=90, check=check)
            except asyncio.TimeoutError:
                self.flipable = False
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


class NodeFlipbook(Flipbook):
    """Flipbook for flipping through and editing
    permission nodes."""

    def __init__(self, ctx, cfg):
        self.cfg = cfg
        self.nodes = cfg['nodes']
        super().__init__(ctx, list(self.nodes), entries_per_page=8, title='Dict Book',
                         color=discord.Color.gold())
        self.current_entries = []
        self.curr_editing = None
        self.curr_entry_name = ''
        self.curr_index = 0
        self.current_page = 0
        self.selectionBttns = [
            ('\u0031\u20E3', self.draw_entry_content(0)),
            ('\u0032\u20E3', self.draw_entry_content(1)),
            ('\u0033\u20E3', self.draw_entry_content(2)),
            ('\u0034\u20E3', self.draw_entry_content(3)),
            ('\u0035\u20E3', self.draw_entry_content(4)),
            ('\u0036\u20E3', self.draw_entry_content(5)),
            ('\u0037\u20E3', self.draw_entry_content(6)),
            ('\u0038\u20E3', self.draw_entry_content(7))
        ]
        self.entryViewBttns = [
            ('\N{Squared Up With Exclamation Mark}', self.draw_page(self.current_page)),
            ('\N{PENCIL}', self.edit_entry()),
            ('\N{BOMB}', self.delete_entry())
        ]

    async def draw_page(self, page, first=False):
        if page < 0 or page > (self.pages - 1):
            return

        self.current_page = page
        self.current_entries = self.flip_entries(page)
        content = []
        for i, e in enumerate(self.current_entries):
            content.append(f'#{i+1}: \'{e}\'')

        if self.title:
            self.embed.title = self.title

        if self.pages > 1:
            self.embed.set_footer(text=f'Page {page} of {self.pages - 1}')
        else:
            self.embed.set_footer(text=u'Got it all on one page! ╭( ･ㅂ･)و')

        self.embed.description = '\n'.join(content)

        if first:
            self.msg = await self.ctx.send(embed=self.embed)
        else:
            await self.msg.edit(embed=self.embed)
            await self.msg.clear_reactions()

        if self.flipable:
            for (bttn, _) in self.bttns:
                await self.msg.add_reaction(bttn)

        for (bttn, _) in self.selectionBttns[:len(content)]:
            await self.msg.add_reaction(bttn)

    async def draw_entry_content(self, index):
        self.curr_entry_name = self.current_entries[index]
        entryEmbed = discord.Embed(color=discord.Color.dark_blue())
        entryEmbed.description = f'Entry for {self.curr_entry_name}:'
        self.curr_editing = self.nodes[self.curr_entry_name]
        if self.curr_entry_name.startswith('spec:'):
            entryEmbed.add_field('Prompt:', self.curr_editing[1])
            entryEmbed.add_field('Value:', self.curr_editing[0])
        else:
            entryEmbed.add_field('Minimum required role:',
                                 self.curr_editing['role'], inline=False)
        await self.msg.clear_reactions()
        await self.msg.edit(embed=entryEmbed)
        await self.msg.add_reaction('\N{PENCIL}')
        await self.msg.add_reaction('\N{Squared Up With Exclamation Mark}')
        await self.msg.add_reaction('\N{BOMB}')

    async def edit_entry(self):
        if self.curr_entry_name.startswith('spec:'):
            if type(self.curr_editing[0]) is bool:
                self.curr_editing[0] = await promptConfirm(self.ctx, f'> {self.curr_editing[1]}')
            else:
                self.curr_editing[0] = await promptInput(self.ctx, f'> {self.curr_editing[1]}')
        else:
            change_roles = await promptConfirm(self.ctx, '> Do you wish to edit required roles?')
            if change_roles:
                req_role = await promptInput(self.ctx, '> Please enter the minimum role'
                                             f' required for {self.curr_entry_name}!'
                                             'To clear role requirements, enter: \'\'')
                if req_role == "''":
                    self.curr_editing['role'] = ''
                else:
                    self.curr_editing['role'] = req_role
            change_chan_limit = await promptConfirm(self.ctx, '> Do you wish to edit where '
                                                    f'{self.curr_entry_name} is allowed?')
            if change_chan_limit:
                chan_limit = await promptInput(self.ctx, '> Please enter all IDs of the channels '
                                               f'where you wish {self.curr_entry_name} to be allowed!\n'
                                               'Delimited by spaces only!\n'
                                               'To clear channel limits, enter: \'\'')
                if chan_limit == "''":
                    self.curr_editing['channels'] = []
                else:
                    self.curr_editing['channels'] = list(map(int, chan_limit.split()))
        await self.draw_entry_content(self.curr_index)

    async def delete_entry(self):
        confirmation = await promptConfirm(self.ctx, '> Do you really wish to delete the entry '
                                           f'for {self.curr_entry_name}?\n'
                                           f'< This will make {self.curr_entry_name} bot owner only! >')
        if confirmation:
            del self.nodes[self.curr_entry_name]
            await sendMarkdown(self.ctx, f'> {self.curr_entry_name} deleted!')

    async def flip_off(self):
        self.flipable = False
        await self.msg.clear_reactions()
        await self.cfg.save()
        await self.msg.edit(embed=None,
                            content='```markdown\n# Dict Book closed, changes saved!\n```')

    async def info(self):
        if self.helping:
            self.helping = False
            await self.draw_page(self.current_page)
        else:
            self.helping = True
            content = [
                'Node Book control manual:',
                ' ',
                'To flip through the pages (if there is more than one):',
                'Flip backwards: 👈',
                'Flip forwards:  👉',
                'Flip Charfred off: 🖕 (closes Node Book AND saves changes)',
                'Toggle this help: ❔',
                ' ',
                'There are number-block emoji for each entry on the page:',
                'Go to content view of entry #1: 1️⃣',
                ' ',
                'To edit an entry, go to it\'s content view, then:',
                'Edit entry: ✏️ (will trigger entry prompts)',
                'Delete entire entry: 💣 (will trigger a confirm prompt)',
                'Return to entry page: 🆙',
                ' ',
                'Remember to flip Charfred off to save any changes!'
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

            for (bttn, func) in chain(self.bttns, self.selectionBttns, self.entryViewBttns):
                if str(reaction.emoji) == bttn:
                    self.action = func
                    return True
            return False

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=120, check=check)
            except asyncio.TimeoutError:
                try:
                    await self.msg.clear_reactions()
                except:
                    pass
                finally:
                    break
            else:
                try:
                    await self.msg.remove_reaction(reaction, user)
                except:
                    pass
            await self.action()
