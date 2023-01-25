"""Play a sound based on a channel point redemption."""

from audio import audio_utils
from plugins._base_plugins import BaseRedemptionPlugin


class SoundRedemptionCommand(BaseRedemptionPlugin):
    """Play a sound based on a channel point redemption."""

    COMMAND = 'sound'

    async def run(self) -> None:
        """Play a sound."""
        username = self.user['name']
        sound = self.command_args[0]

        await self.send_message(f'{username} played a sound: {sound}!')
        await audio_utils.play(sound)
