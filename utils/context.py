import re
from asyncio import TimeoutError

from discord.ext import commands

from utils import splitup, ConfirmationPrompt


class CharfredContext(commands.Context):
    def prompt_check(self, msg):
        return msg.author.id == self.author.id and msg.channel.id == self.channel.id

    async def send(
        self, msg=None, deletable=True, embed=None, codeblocked=False, **kwargs
    ):
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

    async def sendmarkdown(self, msg, deletable=True, log=None, **kwargs) -> None:
        """Wrap a message in markdown codeblocks and send if off.

        Parameters
        ----------
        msg
            message to send
        deletable, optional
            include in command output deletion chain, by default True
        log, optional
            if logger is provided, will also send message to log, by default None
        """

        if log:
            log.info(msg)
        return await self.send(
            f'```markdown\n{msg}\n```', deletable=deletable, codeblocked=True, **kwargs
        )

    async def promptinput(self, prompt: str, timeout: int = 120, deletable=True):
        """Prompt for text input.

        Returns a tuple of acquired input,
        reply message, and boolean indicating prompt timeout.
        """

        await self.sendmarkdown(prompt, deletable)
        try:
            r = await self.bot.wait_for(
                'message', check=self.prompt_check, timeout=timeout
            )
        except TimeoutError:
            await self.sendmarkdown('> Prompt timed out!', deletable)
            return (None, None, True)
        else:
            return (r.content, r, False)

    async def promptreaction(
        self,
        prompt: str,
        emoji: str,
        success_text: str = None,
        failure_text: str = None,
        timeout: int = 60,
        deletable=True,
        author_only=True,
    ) -> bool:
        """Prompt for a specific reaction emoji.

        Parameters
        ----------
        prompt
            message to prompt with
        emoji
            emoji to wait for
        success_text, optional
            override prompt message on success if given, by default None
        failure_text, optional
            override prompt message on failure if given, by default None
        timeout, optional
            how long to wait in seconds, by default 60
        deletable, optional
            include in command output deletion chain, by default True
        author_only, optional
            whether or not only the original command author's
            reaction is accepted, by default True

        Returns
        -------
            whether the prompt was reacted to or not
        """

        msg = await self.sendmarkdown(prompt, deletable=deletable)
        await msg.add_reaction(emoji)

        def _check(reaction, user):
            if reaction.message.id != msg.id:
                return False

            if author_only:
                return str(reaction.emoji) == emoji and user == self.author
            else:
                return str(reaction.emoji) == emoji and not user.bot

        try:
            await self.bot.wait_for('reaction_add', timeout=timeout, check=_check)
        except TimeoutError:
            await msg.clear_reactions()
            if failure_text:
                await msg.edit(content=f'```markdown\n{failure_text}\n```')
            return False
        else:
            await msg.clear_reactions()
            if success_text:
                await msg.edit(content=f'```markdown\n{success_text}\n```')
            return True

    async def promptconfirm(self, prompt: str, timeout: int = 120, deletable=True):
        """Prompt for confirmation.

        Returns a triple of acquired confirmation,
        reply message, and boolean indicating prompt timeout.
        """

        view = ConfirmationPrompt(self, timeout, cancel_emoji='❌')

        msg = await self.sendmarkdown(prompt, deletable, view=view)
        await view.wait()

        if view.confirmed is None:
            view.clear_items()
            await msg.edit(content='```md\n> Prompt timed out!\n```', view=view)
            return None
        else:
            return view.confirmed

    async def promptconfirm_or_input(
        self, prompt: str, timeout: int = 120, deletable=True, confirm=True
    ):
        """Prompt for confirmation or input at the same time.

        Instead of 'yes/no' this lets your prompt for 'yes/input' or 'no/input',
        depending on the 'confirm' kwarg.

        Returns a 3 tuple of input, reply message object
        and boolean indicating prompt timeout.

        'input' will be None, if 'yes' for confirm=True (the default),
        or 'no' for confirm=False.
        """

        await self.sendmarkdown(prompt, deletable)
        try:
            r = await self.bot.wait_for(
                'message', check=self.prompt_check, timeout=timeout
            )
        except TimeoutError:
            await self.sendmarkdown('> Prompt timed out!', deletable)
            return (None, True)
        else:
            if confirm:
                pat = '^(y|yes)'
            else:
                pat = '^(n|no)'

            if re.match(pat, r.content, flags=re.I):
                return (None, False)
            else:
                return (r.content, False)
