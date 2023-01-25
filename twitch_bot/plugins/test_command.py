"""Test plugin."""

from plugins._base_plugins import BaseCommandPlugin


class TestCommand(BaseCommandPlugin):
    """Test plugin.

    Used to confirm the bot is working.
    """

    COMMAND = 'test'

    async def run(self) -> None:
        """Test."""
        await self.send_message('Test command plugin has been run.')
