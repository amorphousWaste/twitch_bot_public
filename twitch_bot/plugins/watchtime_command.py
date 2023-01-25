"""Watch Time plugin."""

import utils

from plugins._base_plugins import BaseCommandPlugin


class WatchTimeCommand(BaseCommandPlugin):
    """Watch time plugin."""

    COMMAND = 'watchtime'

    async def run(self) -> None:
        """Stream watch time."""
        watch_time = await utils.get_watch_time(self.bot, self.user)
        await self.send_message(f'You have been watching for: {watch_time}')
