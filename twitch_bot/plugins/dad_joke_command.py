"""Dad joke plugin."""

import server_utils

from plugins._base_plugins import BaseCommandPlugin


class DadJokeCommand(BaseCommandPlugin):
    """Dad joke plugin."""

    COMMAND = 'dadjoke'

    async def run(self) -> None:
        """Dad jokes provided by icanhazdadjoke.com."""
        url = 'https://icanhazdadjoke.com/'
        headers = {
            'User-Agent': 'https://github.com/amorphousWaste/twitch_bot',
            'Accept': 'application/json',
        }

        _, response = await server_utils.get_request(url, headers)
        if not response:
            return -1

        await self.send_message(response['joke'])
