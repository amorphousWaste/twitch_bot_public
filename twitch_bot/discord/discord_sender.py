"""Discord integration."""

import json

import server_utils

from configs import config_utils
from log import LOG


async def send_discord_message(message: str) -> None:
    """Send a message to Discord.

    Args:
        message (str): Message to send.
    """
    config = await config_utils.load_config_file('bot_config')
    username = config.get('discord_username')
    url = config.get('discord_url')

    headers = {'Content-type': 'application/json'}

    data = {'username': username, 'avatar_url': '', 'content': message}
    json_data = json.dumps(data)

    response = await server_utils.post_request(url, json_data, headers)
    LOG.debug(f'Discord response: {response}')


async def send_online_announcement(channel_data: dict) -> None:
    """Send the stream online announcement via discord.

    Args:
        channel_data (dict): Twitch channel data.
    """
    game = channel_data['game_name']
    message = (
        '@everyone Grab a blanket, get comfy, and come on by for some '
        f'{game}! https://www.twitch.tv/descvert'
    )
    await send_discord_message(message)
