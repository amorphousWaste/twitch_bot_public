"""Pet plugin."""

from plugins._base_plugins import BaseCommandPlugin, BaseRedemptionPlugin


class PetCommand(BaseCommandPlugin):
    """Pet plugin."""

    COMMAND = 'pet'

    async def run(self) -> None:
        """Interaction with the Pet project."""
        if not self.command_args:
            await self.send_message(
                'Please provide an interaction: clean, eat, exercise, learn, '
                'pet, play, or speak.'
            )
            return -1

        await self.bot.tcp_server.publish_message(
            'action {}'.format(self.command_args[0])
        )


class PetHatRedemption(BaseRedemptionPlugin):
    """Pet plugin for handling hat redemption rewards."""

    COMMAND = 'hat_for_pet'

    async def run(self) -> None:
        """Put a hat on the pet."""
        username = self.user['name']
        hat = self.command_args[-1]

        await self.send_message(f'{username} put a {hat} hat on the pet!')
        await self.bot.tcp_server.publish_message(
            'hat {}'.format(self.command_args[0])
        )


class PetGlassesRedemption(BaseRedemptionPlugin):
    """Pet plugin for handling glasses redemption rewards."""

    COMMAND = 'glasses_for_pet'

    async def run(self) -> None:
        """Put glasses on the pet."""
        username = self.user['name']
        glasses = self.command_args[-1]

        await self.send_message(
            f'{username} put {glasses} glasses on the pet!'
        )
        await self.bot.tcp_server.publish_message(
            'glasses {}'.format(self.command_args[0])
        )
