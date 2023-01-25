#!/usr/bin/env python
"""Run the bot."""

import argparse
import asyncio

import ngrok

from auth import Auth
from bot import TwitchBot
from chat.chat_connection import ChatConnection
from chat.chat_receiver import ChatReceiver
from eventsub import eventsub_server
from eventsub.eventsub import EventSub
from init import CACHE
from log import LOG
from obs.obs_connection import OBSConnection
from pubsub.pubsub import PubSub
from tcp_utils import TCPServer
from timer.timer import Timer


def get_args() -> dict:
    """Get the args from argparse.

    Returns:
        args (dict): Arguments from argparse.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--channel', help='Set the channel to connect the bot to.'
    )

    parser.add_argument(
        '--notimers',
        help='Run the bot without timer events.',
        action='store_true',
    )

    parser.add_argument(
        '--nopubsub',
        help='Run the bot without pubsub events.',
        action='store_true',
    )

    parser.add_argument(
        '--noeventsub',
        help='Run the bot without eventsub events.',
        action='store_true',
    )

    parser.add_argument(
        '--nochat',
        help='Run the bot without connecting to chat.',
        action='store_true',
    )

    parser.add_argument(
        '--noobs',
        help='Run the bot without connecting to OBS.',
        action='store_true',
    )

    args = parser.parse_args()
    return vars(args)


async def end_tasks(tasks: list) -> None:
    """End async tasks.

    Args:
        tasks (list): List of async tasks.
    """
    for task in tasks:
        task.cancel()


async def init() -> None:  # noqa
    """Initialize the bot."""
    # Get the arguments.
    args = get_args()

    # Create a cache of user names in chat.
    if not await CACHE.exists('users'):
        await CACHE.add('users', data=[])

    # Create a cache of chatters for stats.
    if not await CACHE.exists('chatters'):
        await CACHE.add('chatters', data=[])

    # Create and initialize the authorization object.
    authorization = await Auth().init()

    # Create and initialize the connection to Twitch.
    chat_connection = await ChatConnection().init(
        authorization, channel=args.get('channel', '')
    )

    # Initialize the OBS connection.
    obs_connection = await OBSConnection().init(authorization)

    # Initialize the TCP server.
    tcp_server = await TCPServer().init()

    # Create and initialize the bot.
    bot = await TwitchBot().init(
        authorization, chat_connection, obs_connection, tcp_server
    )
    message_receiver = ChatReceiver(chat_connection)

    # Create the asynchronous tasks.
    tasks = []

    # Create the TCP server task.
    tasks.append(asyncio.create_task(tcp_server.run()))

    if not args.get('notimers', False):
        # Initialize the timers.
        timer = await Timer().init()
        tasks.append(asyncio.create_task(timer.run()))

    if not args.get('nopubsub', False):
        # Initialize the PubSub receiver.
        pubsub = await PubSub().init(authorization)
        tasks.extend(
            [
                asyncio.create_task(pubsub.run()),
                asyncio.create_task(pubsub.send_heartbeat()),
            ]
        )

    if not args.get('noeventsub', False):
        # Run the ngrok service.
        ngrok_process = await ngrok.Ngrok().init()
        ngrok_thread = await ngrok_process.get_thread()
        ngrok_thread.start()

        await asyncio.sleep(2)

        # Initialize the EventSub receiver.
        await EventSub().init(authorization)
        flask_thread = await eventsub_server.get_thread()
        flask_thread.start()

    if not args.get('nochat', False):
        # Initialize chat.
        tasks.extend(
            [
                asyncio.create_task(bot.run()),
                asyncio.create_task(message_receiver.run()),
            ]
        )

    if not args.get('noobs', False):
        # Initialize the OBS connection.
        tasks.append(asyncio.create_task(obs_connection.run()))

    if not tasks:
        LOG.error('No tasks to run, please check your arguments.')
        return

    # Add the cache cleaning task.
    tasks.append(asyncio.create_task(CACHE.clean_task()))

    try:
        await asyncio.gather(*tasks)

    except KeyboardInterrupt:
        await end_tasks(tasks)
        ngrok_thread.stop()
        flask_thread.stop()


if __name__ == "__main__":
    asyncio.run(init())
