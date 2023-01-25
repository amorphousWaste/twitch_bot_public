"""Tools for working with the BetterTTV API.

Note: This API is undocumented, but appears to be valid for public use.
"""

from server_utils import get_request


async def get_bttv_emotes(twitch_id: int or str) -> dict:
    """Get a user's emotes from BTTV.

    Args:
        twitch_id (int, str): Twitch user ID.

    Returns:
        (dict): Emote data.
    """
    _, data = await get_request(
        f'https://api.betterttv.net/3/cached/users/twitch/{twitch_id}', {}
    )

    emoticons = []

    channel_emote_data = data.get('channelEmotes', [])
    if channel_emote_data:
        conformed_channel_emote_data = await adapt_bttv_data(
            channel_emote_data
        )
        emoticons.extend(conformed_channel_emote_data)

    shared_emote_data = data.get('sharedEmotes', [])
    if shared_emote_data:
        conformed_shared_emote_data = await adapt_bttv_data(shared_emote_data)
        emoticons.extend(conformed_shared_emote_data)

    return emoticons


async def adapt_bttv_data(bttv_data: list[dict]) -> list[dict]:
    """Adapt the data from BTTV to work with the Emote object.

    Args:
        bttv_data (list[dict]): Emote data from BTTV.

    Returns:
        conformed_bttv_data (list[dict]): Conformed data from BTTV.
    """
    conformed_bttv_data = []

    for emote in bttv_data:
        emote_id = emote['id']
        conformed_bttv_data.append(
            {
                'id': emote_id,
                'name': emote['code'],
                'emote_type': 'bttv',
                'emote_set_id': 0,
                'images': {
                    'url_4x': f'https://cdn.betterttv.net/emote/{emote_id}/3x'
                },
            }
        )

    return conformed_bttv_data
