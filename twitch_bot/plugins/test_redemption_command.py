"""Test redemption command plugin."""

from plugins._base_plugins import BaseRedemptionPlugin


class TestRedemptionCommand(BaseRedemptionPlugin):
    """Test redemption command plugin."""

    COMMAND = 'Test_Reward'

    async def run(self) -> None:
        """Test redemption."""
        username = self.user['name']
        await self.send_message(f'{username} redeemed a the {self.command}!')
