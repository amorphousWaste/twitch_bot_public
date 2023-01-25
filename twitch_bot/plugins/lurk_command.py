"""Lurk plugin."""

from plugins._base_plugins import BaseCommandPlugin


class LurkCommand(BaseCommandPlugin):
    """Lurk plugin.

    Used to indicate lurking.
    """

    COMMAND = 'lurk'

    async def run(self) -> None:
        """Lurk message."""
        await self.send_message(
            '/me {} continues to watch the stream in ultimate '
            'comfy-ness.'.format(self.user['name'])
        )


class UnlurkCommand(BaseCommandPlugin):
    """Unlurk plugin.

    Used to indicate a person is no longer lurking.
    """

    COMMAND = 'unlurk'

    async def run(self) -> None:
        """Unlurk message."""
        await self.send_message(
            '/me {} is no longer lurking but still remains comfy.'.format(
                self.user['name']
            )
        )
