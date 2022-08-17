from typing import Any, List, Optional
import discord


class ConfirmationButton(discord.ui.Button):
    def __init__(
        self,
        confirmed: bool,
        button_style: discord.ButtonStyle,
        label: str | None = None,
        emoji: str | None = None,
        row: int | None = 0,
        reply_text: str | None = None,
        ephemeral: bool = False,
    ):
        super().__init__(style=button_style, label=label, emoji=emoji, row=row)
        self.confirmed = confirmed
        self.reply_text = reply_text
        self.ephemeral = ephemeral

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view = self.view
        view.confirmed = self.confirmed
        view.clear_items().stop()
        await interaction.response.edit_message(
            content=f'```md\n{self.reply_text}\n```', view=view
        )


class SelectionView(discord.ui.View):
    def __init__(
        self,
        ctx,
        select_options: List[discord.SelectOption],
        *,
        placeholder: str | None,
        author_only: bool = True,
        timeout: Optional[float] = 180,
    ):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.author_only = author_only
        self.select = discord.ui.Select(
            placeholder=placeholder, options=select_options, row=0
        )
        self.select.callback = self.callback
        self.add_item(self.select)
        self.button = discord.ui.Button(
            style=discord.ButtonStyle.gray, emoji='❌', row=1
        )
        self.button.callback = self.callback
        self.add_item(self.button)

    async def callback(self, interaction: discord.Interaction):
        self.stop()
        await interaction.response.send_message(content='Got it!', ephemeral=True)

    @property
    def values(self):
        return self.select.values

    async def on_timeout(self) -> None:
        self.clear_items()

        await self.msg.edit(content='```md\n> Timed out\n```', view=self)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.author_only:
            return self.ctx.author.id == interaction.user.id
        else:
            return True


class ConfirmationPrompt(discord.ui.View):
    def __init__(
        self,
        ctx,
        timeout: float = 180,
        author_only: bool = False,
        confirm_label: str | None = None,
        cancel_label: str | None = None,
        confirm_emoji: str | None = '👍',
        cancel_emoji: str | None = None,
        confirm_text: str = '# Confirmed',
        cancel_text: str = '> Cancelled',
        ephemeral: bool = False,
    ):
        """Confirmation Prompt View, with 1 to 2 buttons.

        Confirm button is always provided,
        cancel button is only provided if cancel_label and/or cancel_emoji are defined.

        Parameters
        ----------
        ctx
            context in which this view exists
        timeout, optional
            how long to listen for interaction, by default 180
        author_only, optional
            whether only the ctx message author can interact, by default False
        confirm_label, optional
            text on confirm button, by default None
        cancel_label, optional
            text on cancel button, by default None
        confirm_emoji, optional
            emoji on confirm button, by default '👍'
        cancel_emoji, optional
            emoji on cancel button, by default None
        confirm_text, optional
            response to send when confirm is pressed, by default 'Confirmed'
        cancel_text, optional
            response to send when cancel is pressed, by default 'Cancelled'
        ephemeral, optional
            whether the response can only be seen by the user who pressed the button,
            by default False
        """
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.confirmed = None
        self.author_only = author_only

        confirm_button = ConfirmationButton(
            True,
            discord.ButtonStyle.primary,
            confirm_label,
            confirm_emoji,
            0,
            confirm_text,
            ephemeral,
        )
        self.add_item(confirm_button)

        if cancel_label or cancel_emoji:
            cancel_button = ConfirmationButton(
                False,
                discord.ButtonStyle.danger,
                cancel_label,
                cancel_emoji,
                0,
                cancel_text,
                ephemeral,
            )
            self.add_item(cancel_button)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.author_only:
            return self.ctx.author.id == interaction.user.id
        else:
            return True
