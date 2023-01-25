"""Account age plugin."""

from log import LOG

from datetime import datetime

import api
import utils

from plugins._base_plugins import BaseCommandPlugin


class AccountAgeCommand(BaseCommandPlugin):
    """Account age plugin."""

    COMMAND = 'accountage'

    async def run(self) -> None:
        """The the user's account age."""
        user_name = self.user['name']
        user_data = await api.get_user_data(self.bot.auth, user_name)
        if not user_data:
            LOG.warning(f'No data for {user_name}.')
            return -1

        created_at = user_data.get('created_at', None)
        if not created_at:
            return -1

        created_at_dt = await utils.parse_datetime(created_at)
        delta = datetime.now() - created_at_dt
        dt_string = await utils.display_from_seconds(delta.total_seconds())

        await self.send_message(f'Your account is {dt_string} old.')
