"""Stream marker plugin."""

import api

from plugins._base_plugins import BaseCommandPlugin


class StreamMarkerCommand(BaseCommandPlugin):
    """Stream marker plugin."""

    ALLOW = ['mod']
    COMMAND = 'mark'

    async def run(self) -> None:
        """Create a stream marker."""
        description = ' '.join(self.command_args) if self.command_args else ''

        data = await api.create_marker(
            self.bot.auth, self.bot.broadcaster_id, description
        )
        if not data:
            await self.send_message('Could not create marker.')
            return -1

        time = data.get('position_seconds', '')
        await self.send_message(f'Stream marker created at: {time}.')
