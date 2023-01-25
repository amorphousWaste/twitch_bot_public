"""Timer."""

import asyncio

from init import EVENT_QUEUE
from log import LOG
from timer.timer_events import TimerEvent


class Timer(object):
    """Timer."""

    def __init__(self) -> None:
        """Init."""
        super(Timer, self).__init__()

    async def init(self, interval: int = 60) -> object:
        """Async init.

        Args:
            interval (int): Time in seconds to create a timer event.
                Default is 60 (1 minute).
        """
        self.interval = interval

        return self

    async def run(self) -> None:
        """Create an event every time the interval expires."""
        LOG.debug('Running timer loop.')
        self.running = True

        while self.running:
            await asyncio.sleep(self.interval)

            LOG.debug('Timer is up, adding to queue.')
            event = await TimerEvent().init(self.interval)
            await EVENT_QUEUE.put(event)

        LOG.debug('Timer no longer running.')
