"""Follow age plugin."""

import utils

from plugins._base_plugins import BaseCommandPlugin


class FollowAgeCommand(BaseCommandPlugin):
    """Follow age plugin."""

    COMMAND = 'followage'

    async def run(self) -> None:
        """Show the folow age for the user."""
        display_time = await utils.get_follow_age(self.user['id'], self.bot)
        if not display_time:
            msg = 'You don\'t appear to be following yet.'
        else:
            msg = f'You have been following for: {display_time}'

        await self.send_message(msg)
