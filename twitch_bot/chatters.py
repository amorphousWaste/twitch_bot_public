"""Work with chatters data."""

import api


class Chatters(object):
    """Chatters Object.

    This is used to get and parse the chatters in a stream.
    """

    def __init__(self) -> None:
        """Init."""
        super(Chatters, self).__init__()

    async def init(self, channel_name: str) -> object:
        """Async init.

        Args:
            channel_name (str): Channel to get the chatters for.
        """
        self.channel_name = channel_name

        await self.refresh_chatters()

        return self

    async def refresh_chatters(self):
        """Refresh the chatters data."""
        # Get the data from Twitch
        data = await api.get_chatters(self.channel_name)

        self.admins = data.get('admins', [])
        self.broadcaster = data.get('broadcaster', [])
        self.global_mods = data.get('global_mods', [])
        self.moderators = data.get('moderators', [])
        self.staff = data.get('staff', [])
        self.viewers = data.get('viewers', [])
        self.vips = data.get('vips', [])

        self.chatters = (
            self.admins
            + self.broadcaster
            + self.global_mods
            + self.moderators
            + self.staff
            + self.viewers
            + self.vips
        )

        self.chatter_count = len(self.chatters)
