"""Loyalty Points plugins."""

import api

from init import CACHE

from plugins._base_plugins import BaseCommandPlugin, BaseIntervalPlugin


class UpdateLoyalty(BaseIntervalPlugin):
    """Update loyalty plugin.

    Used to tell the streamer to save their work.
    """

    ALLOWED = ['bot']
    COMMAND = 'update_loyalty'
    INTERVAL = 10

    async def run(self) -> None:
        """Uptdate the amount of loyalty points for everyone in the chat."""
        users_cache = await CACHE.get('users')
        usernames = users_cache.data
        subscribers = await api.get_subscribers(self.bot.auth)

        for username in usernames:
            event = 'subscriber_view' if username in subscribers else 'view'

            await self.bot.loyalty_manager.add_loyalty_points_for_event(
                username, event
            )


class RedeemLoyalty(BaseCommandPlugin):
    """Redeem rewards for loyalty points."""

    COMMAND = 'redeem'

    async def run(self) -> None:
        """Redeem loyalty points."""
        redemptions = await self.bot.loyalty_manager.get_redemptions()

        if not self.command_args:
            await self.send_message(
                f'Please enter a reward to redeem: {redemptions}'
            )
            return False

        username = self.user['name']
        redemption = ' '.join(self.command_args)

        if redemption not in redemptions:
            await self.bot.connection.send_message(
                f'Redemption "{redemption}" not found.'
            )
            return

        loyalty_points = await self.get_loyalty_points(username)
        redemption_cost = redemptions[redemption]

        if loyalty_points < redemption_cost:
            await self.bot.connection.send_message(
                f'Cannot afford redemption "{redemption}" '
                f'({loyalty_points} < {redemption_cost}).'
            )
            return

        await self.bot.loyalty_manager.redeem_loyalty_points(
            username, redemption
        )

        await self.bot.connection.send_message(
            f'{username} redeemed "{redemption}" for {loyalty_points} '
            'points.'
        )


class CheckLoyalty(BaseCommandPlugin):
    """Check loyalty points."""

    COMMAND = 'loyalty'

    async def run(self) -> None:
        """Check loyalty points."""
        username = self.user['name']

        loyalty_points = await self.bot.loyalty_manager.get_loyalty_points(
            username
        )

        await self.send_message(f'{username} has {loyalty_points} points.')


class RefundLoyalty(BaseCommandPlugin):
    """Refund loyalty points."""

    ALLOWED = ['bot']
    COMMAND = 'refund'

    async def run(self) -> None:
        """Refund loyalty points."""
        if (
            not self.command_args
            or len(self.command_args) <= 2
            or len(self.command_args) > 2
        ):
            await self.send_message(
                'Please enter a user and amount to refund.'
            )
            return False

        username = self.command_args[0].strip('@')
        loyalty_points = int(self.command_args[1])

        await self.bot.loyalty_manager.add_loyalty_points(
            username, loyalty_points
        )

        await self.send_message(
            f'{username} has been refunded {loyalty_points} points.'
        )
