"""About Bot plugin."""

from plugins._base_plugins import BaseCommandPlugin


class AboutBotCommand(BaseCommandPlugin):
    """About Bot plugin."""

    COMMAND = 'aboutbot'

    async def run(self) -> None:
        """About the bot."""
        await self.send_message(
            'I am an Open Source Python Twitch Bot soon to be available '
            'on Github.'
        )

        # self.send_message(
        #     'I am an Open Source Python Twitch Bot soon to be available '
        #     'here: https://github.com/amorphousWaste/twitch_bot'
        # )
