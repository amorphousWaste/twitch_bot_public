"""Functions for getting Twitch Data."""

import hashlib
from typing import Callable, Optional

from configs import config_utils
from init import CACHE
from server_utils import get_request, patch_request, post_request


def check_cache(func: Callable) -> Callable:
    """Decorator to check if the API call has been cached.

    This is only applicable if the arguments are the same as well.
    """

    async def wrapper(*args: list, **kwargs: dict) -> dict or list:
        """Check and return cached data if it exists.

        Otherwise, call the API, cache the data, and return the data.

        Args:
            args (list): Arguments.
            kwargs (dict): Additional keyword arguments.

        Returns:
            data (dict or list): Data from the API call.
        """
        api_cache = await CACHE.get('api')
        if not api_cache:
            api_cache = await CACHE.add('api', {}, 360)

        func_name = func.__name__

        if func_name not in api_cache.data:
            api_cache.data[func_name] = {}

        # Convert the arguments to a string and hash it for comparison.
        all_args = ','.join([str(a) for a in args]) + ','.join(
            [f'{k}:{v}' for (k, v) in kwargs.items()]
        )
        args_hash = hashlib.md5(all_args.encode('utf-8'))

        # If the function has been called before and the argument hash matches,
        # load the cached data.
        if args_hash in api_cache.data[func_name]:
            data = api_cache.data[func_name][args_hash]

        # Otherwise, call the function and cache the returned data.
        else:
            data = await func(*args, **kwargs)
            api_cache.data[func_name][args_hash] = data

        return data

    return wrapper


@check_cache
async def get_channel_data(auth: object, channel_name: str) -> dict:
    """Get the information about a channel.

    Channel name is case sensative.

    Args:
        auth (Auth): App access info class.
        channel_name (str): Channel name.

    Returns:
        (dict): Channel data.
    """
    url = 'https://api.twitch.tv/helix/search/channels'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.bearer}',
    }
    params = {'query': channel_name}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.bearer}'
        response_code, data = await get_request(url, headers, params)

    # Query returns all matching broadcaster_logins so an additional filter
    # is needed to grab the exact one.
    channel_data = {}
    for channel in data.get('data', []):
        if channel.get('broadcaster_login', '').lower() == channel_name:
            channel_data = channel
            break

    return channel_data


@check_cache
async def get_user_data(auth: object, username: str) -> dict:
    """Get user data.

    Args:
        auth (Auth): App access info class.
        username (str): Username.

    Returns:
        (dict): User data.
    """
    url = 'https://api.twitch.tv/helix/users'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.bearer}',
    }
    params = {'login': username}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.bearer}'
        response_code, data = await get_request(url, headers, params)

    data_dict = data.get('data', [{}])

    return data_dict[0] if data_dict else {}


@check_cache
async def get_game(
    auth: object,
    game_id: Optional[int or str] = None,
    game_name: Optional[str] = None,
) -> dict:
    """Get the game info from the given ID.

    Please only specify either game_id or game_name. If both are specified,
    only game_id will be used.

    Args:
        auth (Auth): App access info class.
        game_id (int|str, optional): ID for the game.
        game_name (str, optional): Name of the game.
            As per Twitch, name must be an exact match.

    Returns:
        game_data (dict): Game data.
    """
    url = 'https://api.twitch.tv/helix/games'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.bearer}',
    }

    if game_id:
        params = {'id': str(game_id)}
    elif game_name:
        params = {'name': str(game_name)}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.bearer}'
        response_code, data = await get_request(url, headers, params)

    data_dict = data.get('data', [{}])

    return data_dict[0] if data_dict else {}


@check_cache
async def get_channel_emotes(auth: object, channel_name: str) -> dict:
    """Get the emotes for the channel.

    Args:
        auth (Auth): App access info class.
        channel_name (str): Channel name.

    Returns:
        (dict): Emotes data.
    """
    broadcaster_id = await get_channel_data(auth, channel_name)

    url = 'https://api.twitch.tv/helix/chat/emotes'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.bearer}',
    }
    params = {'broadcaster_id': broadcaster_id.get('id')}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.bearer}'
        response_code, data = await get_request(url, headers, params)

    return data.get('data', [])


@check_cache
async def get_global_emotes(auth: object) -> dict:
    """Get the global emotes.

    Args:
        auth (Auth): App access info class.

    Returns:
        (dict): Emotes data.
    """
    url = 'https://api.twitch.tv/helix/chat/emotes/global'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.bearer}',
    }
    params = {}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.bearer}'
        response_code, data = await get_request(url, headers, params)

    return data.get('data', [])


@check_cache
async def get_stream_data(auth: object, user_id: str) -> dict:
    """Get stream data.

    Args:
        auth (Auth): App access info class.
        user_id (str): Twitch user ID.

    Returns:
        (dict): Stream data.
    """
    url = 'https://api.twitch.tv/helix/streams'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.bearer}',
    }
    params = {'user_id': user_id}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.bearer}'
        response_code, data = await get_request(url, headers, params)

    return data.get('data', [])


@check_cache
async def get_follow_count(auth: object, user_id: int = None) -> int:
    """Get the follow count for a user.

    Args:
        auth (Auth): App access info class.
        user (int): Bot owner user ID.

    Returns:
        (int): Follower count.
    """
    url = 'https://api.twitch.tv/helix/users/follows'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.bearer}',
    }
    params = {'to_id': user_id}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.bearer}'
        response_code, data = await get_request(url, headers, params)

    return data.get('total', 0)


@check_cache
async def get_follow_data(
    auth: object, from_id: Optional[str] = None, to_id: Optional[str] = None
) -> dict:
    """Get the follow data for a user.

    This can either be:
        All people the "from_id" follows
        All people following the "to_id"
        Follower date between the "from_id" to the "to_id"

    Args:
        auth (Auth): App access info class.
        from_id (str, optional): Twitch user ID.
        to_id (str): Bot owner user ID.

    Returns:
        (dict): Follow data.
    """
    url = 'https://api.twitch.tv/helix/users/follows'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.bearer}',
    }

    if from_id and not to_id:
        params = {'from_id': from_id}
    elif not from_id and to_id:
        params = {'to_id': to_id}
    else:
        params = {'from_id': from_id, 'to_id': to_id}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.bearer}'
        response_code, data = await get_request(url, headers, params)

    while 'pagination' in data and data.get('pagination'):
        params['after'] = data.get('pagination').get('cursor')

        response_code, new_data = await get_request(url, headers, params)

        data['data'].extend(new_data.get('data'))
        if 'pagination' in new_data:
            cursor = new_data.get('pagination').get('cursor')
            if not cursor:
                break

            data['pagination']['cursor'] = cursor
        else:
            break

    data_dict = data.get('data', [{}])

    return data_dict[0] if data_dict else {}


@check_cache
async def get_chatters(channel_name: str) -> dict:
    """Get a dictionary of people chatting in the stream.

    NOTE: This is an undocumented endpoint.

    Args:
        channel_name (str): Channel name.

    Returns:
        dict: Chatters data.
    """
    url = f'https://tmi.twitch.tv/group/user/{channel_name}/chatters'
    headers = {}

    response_code, data = await get_request(url, headers)

    return data.get('chatters', {})


@check_cache
async def get_subscribers(auth: object, user_id: Optional[int] = None) -> list:
    """Get the subscribers for the given broadcaster.

    Args:
        auth (Auth): App access info class.
        user_id (int, optional): User ID to filter results by.

    Returns:
        (list): Subscriber data.
    """
    config = await config_utils.load_config_file('bot_config')
    owner = config.get('owner')
    broadcaster_data = await get_channel_data(auth, owner)

    url = 'https://api.twitch.tv/helix/subscriptions'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.access_token}',
    }
    params = {'broadcaster_id': broadcaster_data.get('id'), 'first': 100}

    if user_id:
        params['user_id'] = user_id

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.access_token}'
        response_code, data = await get_request(url, headers, params)

    while 'pagination' in data:
        params['after'] = data.get('pagination').get('cursor')

        response_code, new_data = await get_request(url, headers, params)

        data['data'].extend(new_data.get('data'))
        if 'pagination' in new_data:
            cursor = new_data.get('pagination').get('cursor')
            if not cursor:
                break

            data['pagination']['cursor'] = cursor
        else:
            break

    return data.get('data', [])


async def create_marker(
    auth: object, user_id: int, description: str = ''
) -> list:
    """Create a stream marker for the given user at the current time.

    Args:
        auth (Auth): App access info class.
        user_id (int): Twitch broadcaster ID.
        description (str): Marker description.

    Returns:
        (list): Subscriber data.
    """
    url = 'https://api.twitch.tv/helix/streams/markers'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.access_token}',
    }
    params = {'user_id': user_id, 'description': description}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.access_token}'
        response_code, data = await get_request(url, headers, params)

    return data.get('data', [])


@check_cache
async def get_schedule(auth: object, segments: Optional[int] = 3) -> dict:
    """Get the stream schedule for the given broadcaster.

    Args:
        auth (Auth): App access info class.
        segments (int, optional): Number of segments to return.

    Returns:
        (dict): Schedule segment data.
    """
    config = await config_utils.load_config_file('bot_config')
    owner = config.get('owner')
    broadcaster_data = await get_channel_data(auth, owner)

    url = 'https://api.twitch.tv/helix/schedule'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.access_token}',
    }
    params = {'broadcaster_id': broadcaster_data.get('id'), 'first': segments}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.access_token}'
        response_code, data = await get_request(url, headers, params)

    return data.get('data', {})


@check_cache
async def get_goals(auth: object) -> list:
    """Get the goals for the given broadcaster.

    Args:
        auth (Auth): App access info class.

    Returns:
        (list): List of goal data.
    """
    config = await config_utils.load_config_file('bot_config')
    owner = config.get('owner')
    broadcaster_data = await get_channel_data(auth, owner)

    url = 'https://api.twitch.tv/helix/goals'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.access_token}',
    }
    params = {'broadcaster_id': broadcaster_data.get('id')}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.access_token}'
        response_code, data = await get_request(url, headers, params)

    return data.get('data', [])


@check_cache
async def get_chat_settings(auth: object) -> dict:
    """Get the chat settings for the given broadcaster.

    Args:
        auth (Auth): App access info class.

    Returns:
        (dict): Dictionary of chat settings data.
    """
    config = await config_utils.load_config_file('bot_config')
    owner = config.get('owner')
    broadcaster_data = await get_channel_data(auth, owner)

    url = 'https://api.twitch.tv/helix/chat/settings'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.access_token}',
    }
    params = {'broadcaster_id': broadcaster_data.get('id')}

    response_code, data = await get_request(url, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.access_token}'
        response_code, data = await get_request(url, headers, params)

    data_dict = data.get('data', [{}])

    return data_dict[0] if data_dict else {}


async def update_chat_settings(auth: object, patch: dict) -> list:
    """Get the goals for the given broadcaster.

    Args:
        auth (Auth): App access info class.
        patch (dict): Field(s) to update and their appropriate value(s).

    Returns:
        (list): List of goal data.
    """
    config = await config_utils.load_config_file('bot_config')
    owner = config.get('owner')
    broadcaster_data = await get_channel_data(auth, owner)

    username = config.get('username')
    bot_user_data = await get_user_data(auth, username)

    url = 'https://api.twitch.tv/helix/chat/settings'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.access_token}',
    }
    params = {
        'broadcaster_id': broadcaster_data.get('id'),
        'moderator_id': bot_user_data.get('id'),
    }

    response_code, data = await patch_request(url, headers, params, patch)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.access_token}'
        response_code, data = await patch_request(url, headers, params, patch)

    data_dict = data.get('data', [{}])

    return data_dict[0] if data_dict else {}


async def ban_user(
    auth: object,
    user_id: int,
    reason: Optional[str] = 'Violation of stream rules.',
    duration: Optional[int] = None,
) -> None:
    """Get the goals for the given broadcaster.

    Args:
        auth (Auth): App access info class.
        user_id (int): Twitch broadcaster ID.
        reason (str, optional): Reason for the ban.
        duration (duration, optional): Length in seconds from 1 to 1,209,600.
            If not given, ban is permanent.

    Returns:
        (list): List of goal data.
    """
    config = await config_utils.load_config_file('bot_config')
    owner = config.get('owner')
    broadcaster_data = await get_channel_data(auth, owner)

    username = config.get('username')
    bot_user_data = await get_user_data(auth, username)

    url = 'https://api.twitch.tv/helix/moderation/bans'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.access_token}',
    }
    params = {
        'broadcaster_id': broadcaster_data.get('id'),
        'moderator_id': bot_user_data.get('id'),
    }
    data_param = {'data': {'user_id': str(user_id), 'reason': reason}}
    if duration:
        data_param.update({'duration': duration})

    response_code, data = await post_request(url, data_param, headers, params)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.access_token}'
        response_code, data = await post_request(
            url, data_param, headers, params
        )

    data_dict = data.get('data', [{}])

    return data_dict[0] if data_dict else {}


async def update_stream_settings(auth: object, patch: dict) -> list:
    """Update stream information.

    Args:
        auth (Auth): App access info class.
        patch (dict): Field(s) to update and their appropriate value(s).
            Available fields are:
                game_id (str): Game ID or 0.
                broadcaster_language (str): ISO 639-1 two-letter code
                    for a supported stream language.
                title (str): Stream title.
                delay (int): Stream delay. Only available for Partners.

    Returns:
        (list): List of goal data.
    """
    config = await config_utils.load_config_file('bot_config')
    owner = config.get('owner')
    broadcaster_data = await get_channel_data(auth, owner)

    url = 'https://api.twitch.tv/helix/channels'
    headers = {
        'Client-Id': auth.client_id,
        'Authorization': f'Bearer {auth.access_token}',
    }
    params = {
        'broadcaster_id': broadcaster_data.get('id'),
    }

    response_code, data = await patch_request(url, headers, params, patch)

    # If the response code indicates unauthorized,
    # validate the token and try again.
    if response_code == 401:
        await auth.validate_tokens()
        headers['Authorization'] = f'Bearer {auth.access_token}'
        response_code, data = await patch_request(url, headers, params, patch)

    data_dict = data.get('data', [{}])

    return data_dict[0] if data_dict else {}
