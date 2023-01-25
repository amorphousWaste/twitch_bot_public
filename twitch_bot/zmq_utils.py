"""Messaging via ZeroMQ.

Used to communicate with external programs through a
Publisher -> Subscriber relationship.

To create a subscriber, use the following template:
-----

import zmq

CONTEXT = zmq.Context()
SOCKET = CONTEXT.socket(zmq.SUB)
SOCKET.connect('tcp://localhost:5555')

recipient = 'name_of_this_program'
socket.setsockopt_string(zmq.SUBSCRIBE, recipient)

awaiting_message = True
while awaiting_message:
    string = socket.recv_string()
    message = ' '.join(string.split()[1:])
    # Do something with the message below.
"""

import asyncio
import traceback
import zmq

from configs import config_utils
from log import LOG

CONFIG = asyncio.run(config_utils.load_config_file('bot_config'))
CONTEXT = zmq.Context()
SOCKET = CONTEXT.socket(zmq.PUB)

try:
    SOCKET.bind('tcp://*:{port}'.format(port=CONFIG['zmq_port']))
except zmq.error.ZMQError as e:
    LOG.error(
        'Unable to bind ZMQ socket: {}.'.format(getattr(e, 'message', repr(e)))
    )
    # If the level is 'debug', print the traceback as well.
    if LOG.level == 0:
        traceback.print_exc()


async def publish_message(recipient: str, message: str) -> None:
    """Publish a message to an external application via ZMQ.

    Args:
        recipient (str): Intended recipient of the message.
            This acts as the key used by the subscriber(s).
        message (str): Message to send.
    """
    LOG.debug(f'Publishing ZMQ message to {recipient}: {message}')
    try:
        SOCKET.send_string(f'{recipient} {message}')
    except Exception as e:
        LOG.error(
            'Unable to publish message via ZMQ {}'.format(
                getattr(e, 'message', repr(e))
            )
        )
        # If the level is 'debug', print the traceback as well.
        if LOG.level == 0:
            traceback.print_exc()
