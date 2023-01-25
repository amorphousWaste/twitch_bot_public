"""Raid plugin."""

from plugins._base_plugins import BaseCommandPlugin


class RaidCommand(BaseCommandPlugin):
    """Raid plugin."""

    COMMAND = 'raid'

    async def run(self) -> None:
        """Raid."""
        await self.send_message(
            'descveHi comfy DESCVERT raid time descveComfy'
        )
