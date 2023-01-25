"""Tools for working with the FrankerFaceZ API."""

from server_utils import get_request


async def get_ffz_emotes(twitch_id: int or str) -> list[dict]:
    """Get a user's emotes from FFZ.

    Args:
        twitch_id (int, str): Twitch user ID.

    Returns:
        emoticons (list[dict]): Emote data.
    """
    _, data = await get_request(
        f'https://api.frankerfacez.com/v1/room/id/{twitch_id}', {}
    )

    sets = data.get('sets', {})
    if not sets:
        return {}

    emoticons = []
    for set_id in sets:
        set_data = sets.get(set_id, {}).get('emoticons', [])
        conformed_data = await adapt_ffz_data(set_data, set_id)
        emoticons.extend(conformed_data)

    return emoticons


async def adapt_ffz_data(
    ffz_data: list[dict], set_id: int or str
) -> list[dict]:
    """Adapt the data from FFZ to work with the Emote object.

    Args:
        ffz_data (list[dict]): Emote data from FFZ.
        set_id (int, str): FFZ set ID.

    Returns:
        conformed_ffz_data (list[dict]): Conformed data from FFZ.
    """
    conformed_ffz_data = []

    for emote in ffz_data:
        sizes = sorted(emote['urls'].keys())
        url = emote['urls'][sizes[-1]]

        conformed_ffz_data.append(
            {
                'id': emote['id'],
                'name': emote['name'],
                'emote_type': 'ffz',
                'emote_set_id': set_id,
                'images': {'url_4x': f'https:{url}'},
            }
        )

    return conformed_ffz_data
