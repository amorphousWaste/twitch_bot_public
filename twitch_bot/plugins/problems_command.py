"""Problems plugin."""

from plugins._base_plugins import BaseIntervalPlugin


class ProblemsCommand(BaseIntervalPlugin):
    """Problems plugin.

    Used to inform users to report issues.
    """

    ALLOWED = ['bot']
    COMMAND = 'problems'
    INTERVAL = 25

    async def run(self) -> None:
        """Problems message."""
        await self.send_message(
            'Having problems with the stream? Let me know!'
        )
