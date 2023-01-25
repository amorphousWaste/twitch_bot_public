"""Shoutout plugin."""

import api

from plugins._base_plugins import BaseCommandPlugin


class ShoutoutCommand(BaseCommandPlugin):
    """Shoutout plugin.

    Used to shout out and advertise awesome people.
    """

    COMMAND = 'so'

    async def run(self) -> None:
        """Shoutout."""
        if not self.command_args:
            return -1

        channel_data = await api.get_channel_data(
            self.bot.auth, self.command_args[0].lstrip('@').lower()
        )

        if not channel_data:
            await self.send_message(
                'I\'m not sure what you stream, but I\'m sure it\'s cool.'
            )
            return

        url = 'https://www.twitch.tv/{}'.format(
            channel_data.get('broadcaster_login')
        )

        await self.send_message(
            '{} has an awesome channel at {} '
            'They clearly like {}, which is pretty cool.'.format(
                channel_data['display_name'],
                url,
                channel_data['game_name'] or '...things...',
            )
        )
