"""Hydrate plugin."""

from plugins._base_plugins import BaseIntervalPlugin


class HydrateCommand(BaseIntervalPlugin):
    """Hydrate plugin.

    Used to tell the streamer to have a drink of a refreshing beverage.
    """

    ALLOWED = ['bot']
    COMMAND = 'hydrate'
    INTERVAL = 15

    async def run(self) -> None:
        """Hydrate message."""
        await self.send_message(
            'You should have a drink of something refreshing.'
        )
