"""Emote Object."""

import api
from emotes import bttv_utils, ffz_utils
from configs import config_utils


class Emote(object):
    """Emote storage object."""

    def __init__(self):
        """Init."""
        super(Emote, self).__init__()

    async def init(
        self,
        emote_id: str,
        name: str,
        emote_type: str,
        emote_set: int or str,
        url: str,
    ) -> object:
        """Init.

        Args:
            emote_id (int | str): Emote id.
            name (str): Emote name.
            emote_type (str): Emote type.
            emote_set (int | str): Emote set.
            url (str): Emote image url.

        Returns:
            self (Emote): Class instance.
        """
        self.id = str(emote_id)
        self.name = str(name)
        self.type = str(emote_type)
        self.set = emote_set
        self.url = url

        return self

    def __str__(self) -> str:
        return (
            f'id: {self.id}, name: {self.name}, type: {self.type}, '
            f'set: {self.set}, url: {self.url}'
        )

    def __repr__(self) -> str:
        string = self.__str__()
        return f'<Emote object: {string}>'


async def convert_emotes(found_emotes: dict) -> dict:
    """Convert emote data to Emotes.

    Args:
        found_emotes (dict): Emote data from Twitch.

    Returns:
        dict: Dictionary of Emotes.
    """
    emotes = {}
    for data in found_emotes:
        try:
            emotes[data['name']] = await Emote().init(
                data['id'],
                data['name'],
                data.get('emote_type', ''),
                data.get('emote_set_id', 0),
                data.get('images', {}).get('url_4x', ''),
            )
        except KeyError:
            continue

    return emotes


async def get_emotes(
    auth: object, channel_name: str, broadcaster_id: int or str
) -> dict:
    """Get all the emotes associated with the channel.

    Args:
        auth (Auth): App access info class.
        channel_name (str): Username.
        broadcaster_id (int, str): Twitch broadcaster ID.

    Returns:
        (dict): Dictionary of emotes in the form {type: {name: Emote}}
    """
    channel_name = channel_name.lstrip('#')

    emotes = {}
    found_user_emotes = await api.get_channel_emotes(auth, channel_name)
    emotes['user'] = await convert_emotes(found_user_emotes)

    found_global_emotes = await api.get_global_emotes(auth)
    emotes['global'] = await convert_emotes(found_global_emotes)

    config = await config_utils.load_config_file('bot_config')

    if config.get('use_bttv', False):
        found_bttv_emotes = await bttv_utils.get_bttv_emotes(broadcaster_id)
        emotes['bttv'] = await convert_emotes(found_bttv_emotes)

    if config.get('use_ffz', False):
        found_ffz_emotes = await ffz_utils.get_ffz_emotes(broadcaster_id)
        emotes['ffz'] = await convert_emotes(found_ffz_emotes)

    return emotes
