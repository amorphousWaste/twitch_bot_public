"""Uptime plugin."""

import utils

from plugins._base_plugins import BaseCommandPlugin


class UptimeCommand(BaseCommandPlugin):
    """Uptime plugin."""

    COMMAND = 'uptime'

    async def run(self) -> None:
        """Stream uptime."""
        uptime = await utils.get_uptime(self.bot)
        if uptime == 0:
            msg = 'The stream is not live.'
        else:
            msg = f'The stream has been live for: {uptime}'

        await self.send_message(msg)
