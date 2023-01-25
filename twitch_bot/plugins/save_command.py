"""Save plugin."""

from plugins._base_plugins import BaseIntervalPlugin


class SaveCommand(BaseIntervalPlugin):
    """Save plugin.

    Used to tell the streamer to save their work.
    """

    ALLOWED = ['bot']
    COMMAND = 'save'
    INTERVAL = 15

    async def run(self) -> None:
        """Save message."""
        await self.send_message('Remember to save whatever you\'re doing.')
