"""Boop plugin."""

from plugins._base_plugins import BaseCommandPlugin


class BoopCommand(BaseCommandPlugin):
    """Boop plugin.

    Used to indicate lurking.
    """

    COMMAND = 'boop'

    async def run(self) -> None:
        """Boop message."""
        if not self.command_args:
            return -1

        await self.send_message(
            '/me {} boops {}\'s booplesnoot.'.format(
                self.user['name'], self.command_args[0].lstrip('@')
            )
        )
