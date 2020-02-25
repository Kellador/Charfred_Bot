import re
from asyncio import TimeoutError
from discord.ext import commands
from utils import cached_property, splitup


class CharfredContext(commands.Context):
    async def send(self, msg=None, deletable=True, embed=None, codeblocked=False, **kwargs):
        """Helper function to send all sorts of things!

        Messages are automatically split into multiple messages if they're too long,
        and if the codeblocked parameter is True codeblock formatting is
        preserved when such a split occurs.

        Returns the message object for the sent message,
        if a split was performed only the last sent message is returned.
        """
        if (msg is None) or (len(msg) <= 2000):
            outmsg = await super().send(content=msg, embed=embed, **kwargs)
            if deletable:
                try:
                    self.bot.cmd_map[self.message.id].output.append(outmsg)
                except KeyError:
                    pass
                except AttributeError:
                    pass
            return outmsg
        else:
            msgs = splitup(msg, codeblocked)
            for msg in msgs:
                outmsg = await self.send(msg, deletable, codeblocked=codeblocked)
            return outmsg

    async def sendmarkdown(self, msg, deletable=True):
        """Helper function that wraps a given message in markdown codeblocks
        and sends if off.

        Because laziness is the key to great success!
        """
        return await self.send(f'```markdown\n{msg}\n```', deletable=deletable, codeblocked=True)

    async def promptinput(self, prompt: str, timeout: int=120, deletable=True):
        """Prompt for text input.

        Returns a tuple of acquired input,
        reply message, and boolean indicating prompt timeout.
        """
        def check(m):
            return m.author.id == self.author.id and m.channel.id == self.channel.id

        await self.sendmarkdown(prompt, deletable)
        try:
            r = await self.bot.wait_for('message', check=check, timeout=timeout)
        except TimeoutError:
            await self.sendmarkdown('> Prompt timed out!', deletable)
            return (None, None, True)
        else:
            return (r.content, r, False)

    async def promptconfirm(self, prompt: str, timeout: int=120, deletable=True):
        """Prompt for confirmation.

        Returns a triple of acquired confirmation,
        reply message, and boolean indicating prompt timeout.
        """
        def check(m):
            return m.author.id == self.author.id and m.channel.id == self.channel.id

        await self.sendmarkdown(prompt, deletable)
        try:
            r = await self.bot.wait_for('message', check=check, timeout=timeout)
        except TimeoutError:
            await self.sendmarkdown('> Prompt timed out!', deletable)
            return (None, None, True)
        else:
            if re.match('^(y|yes)', r.content, flags=re.I):
                return (True, r, False)
            else:
                return (False, r, False)
