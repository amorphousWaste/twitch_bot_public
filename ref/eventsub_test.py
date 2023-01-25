"""Test eventsub and ngrok."""

import asyncio

from eventsub import eventsub_server
from eventsub.eventsub import EventSub
from log import LOG
from ngrok import Ngrok, get_url


async def init() -> None:
    """Run the ngrok service and Flask server."""
    ngrok = await Ngrok().init()
    await EventSub().init()

    ngrok_thread = await ngrok.get_thread()
    flask_thread = await eventsub_server.get_thread()

    ngrok_thread.start()
    ngrok_thread.join()
    flask_thread.start()
    flask_thread.join()

    ngrok_url = await get_url()
    LOG.debug(f'ngrok URL: {ngrok_url}')

    while True:
        pass


if __name__ == '__main__':
    asyncio.run(init())
