"""Chat event classes."""

import re

from log import LOG


MESSAGE_RE = re.compile(
    r'(@(?P<metadata>.*)\s)?\:(?P<username>\w*)?\!?(?P<address>\w*\@?\w*\.?'
    r'tmi\.twitch\.tv)\s(?P<type>\w+)\s\#?(?P<channel>[\w\*]+)\s?\:?'
    r'(?P<message>.+)?'
)


class Event(object):
    """Base chat event."""

    def __init__(self) -> None:
        """Init."""
        super(Event, self).__init__()


class DummyEvent(Event):
    """Dummy event.

    This is used for events that are captured but do not have a purpose.
    """

    def __init__(self) -> None:
        """Init."""
        super(DummyEvent, self).__init__()

    async def init(self, response: str) -> object:
        """Async init."""
        self.response = response
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A DummyEvent was received: {self}')
