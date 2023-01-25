"""Discord plugin."""

from plugins._base_plugins import BaseIntervalPlugin


class DiscordCommand(BaseIntervalPlugin):
    """Discord plugin.

    Used to plug the discord.
    """

    COMMAND = 'discord'
    INTERVAL = 20

    async def run(self) -> None:
        """Discord message."""
        await self.send_message(
            'Like the stream? Join the Discord! https://discord.gg/CaQjMnP.'
        )
