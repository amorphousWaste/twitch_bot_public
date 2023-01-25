"""Announcement plugin."""

from plugins._base_plugins import BaseIntervalPlugin


class AnnouncementCommand(BaseIntervalPlugin):
    """Announcement plugin.

    Used to announce anything.
    """

    COMMAND = 'announce'
    INTERVAL = 20

    async def run(self) -> None:
        """Announcement message."""
        message = ''

        if message:
            await self.send_message(message)
