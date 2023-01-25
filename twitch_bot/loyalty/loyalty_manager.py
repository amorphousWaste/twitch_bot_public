"""Loyalty Points system."""

import api

from configs import config_utils
from log import LOG


class LoyaltyManager(object):
    """Loyalty Points Manager Class.

    Loyalty points are awarded for certain interactions with stream and can be
    redeemed for special rewards.
    """

    def __init__(self) -> None:
        """Init."""
        super(LoyaltyManager, self).__init__()

    async def init(self, bot: object) -> object:
        """Async init.

        Args:
            bot (TwitchBot): Twitch bot instance.

        Returns:
            self (LoyaltyManager): Class instance.
        """
        self.bot = bot

        # Load the config.
        self.loyalty_config = await config_utils.load_config_file('loyalty')
        self.event_points = self.loyalty_config['event_points']
        self.redemptions = self.loyalty_config['redemptions']

        return self

    async def get_loyalty_points(self, username: str) -> int:
        """Get the loyalty points from the database.

        Args:
            username (str): Username to get the loyalty points for.

        Returns:
            int: Loyalty points.
        """
        loyalty_points = await self.bot.db.read(
            'users', ['loyalty_points'], {'username': username}
        )

        if not loyalty_points:
            loyalty_points = ['0']

        return int(loyalty_points[0])

    async def add_loyalty_points(self, username: str, points: int) -> None:
        """Add the loyalty points to the value in the database.

        Given points will be added to the existing total.

        Args:
            username (str): Username to set the loyalty points for.
            points (int): Loyalty points to add to the existing total.
                This value can be negative to subtract points.
        """
        loyalty_points = await self.get_loyalty_points(username) + points
        await self.bot.db.update(
            'users', {'loyalty_points': loyalty_points}, {'username': username}
        )

    async def add_loyalty_points_for_event(
        self, username: str, event: str, quantity: int = 0
    ) -> None:
        """Add loyalty points for the given event.

        Args:
            username (str): Username to set the loyalty points for.
            event (str): Event name.
            quantity (int): Amount of bits or dollars contributed.
        """
        if event not in self.event_points:
            LOG.warning(f'{event} is not a known loyalty event.')
            return

        if event == 'cheer':
            points = self.event_points['cheer'] * quantity

        elif event == 'tip':
            points = self.event_points['tip'] * quantity

        else:
            points = self.event_points.get(event, 0)

        await self.add_loyalty_points(username, points)

    async def calculate_loyalty_points(self, username: str) -> int:
        """Calculate loyalty points for the given user.

        This is based on time watched and subscriber status. Value may not be
        completely accurate as time during which the user was or was not
        subscribed is not taken into account.

        Args:
            username (str): Username to calculate the loyalty points for.

        Returns:
            points (int): Loyalty points.
        """
        time_watched = await self.bot.db.read(
            'users', ['time_watched'], {'username': username}
        )

        user_data = api.get_user_data(self.bot.auth, username)

        subscriber_info = api.get_subscribers(
            self.bot.auth, user_id=user_data['id']
        )

        if subscriber_info:
            points = time_watched * self.event_points['subscriber_view']
        else:
            points = time_watched * self.event_points['view']

        return points

    async def get_redemptions(self) -> dict:
        """Get the redemptions and their costs.

        Returns:
            (dict): Dictionary of redemptions.
        """
        return self.redemptions

    async def redeem_loyalty_points(
        self, username: str, redemption: str
    ) -> None:
        """Redeem loyalty points for a reward.

        Args:
            username (str): Username to calculate the loyalty points for.
            redemption (str): Name of the redemption.
        """
        await self.add_loyalty_points(username, -self.redemptions[redemption])
