"""Pubsub."""

import asyncio
import json
import traceback
import uuid
import websockets

import api
import auth
import events

from configs import config_utils
from pubsub import pubsub_events

from init import EVENT_QUEUE
from log import LOG


class PubSub(object):
    """Pubsub receiver."""

    PING_INTERVAL = 60

    def __init__(self):
        """Init."""
        super(PubSub, self).__init__()

    async def init(self, authorization: auth.Auth = None) -> object:
        """Async init."""
        self.config = await config_utils.load_config_file('bot_config')
        self.auth = authorization or await auth.Auth().init(self.config)
        self.owner = self.config.get('owner')
        self.username = self.config.get('username')

        self.nonce = str(uuid.uuid1().hex)
        self.topics = await self.get_topics()
        await self.connect()

        return self

    async def get_topics(self) -> list:
        """Get topics from the config.

        Returns:
            topics (list): Pubsub topics with the needed info filled in.
        """
        bot_data = await api.get_user_data(self.auth, self.username)
        bot_user_id = bot_data.get('id')

        channel_data = await api.get_channel_data(self.auth, self.owner)
        channel_id = channel_data.get('id')

        user_data = await api.get_user_data(self.auth, self.owner)
        user_id = user_data.get('id')

        topics_fields = {
            'bot_user_id': bot_user_id,
            'channel_id': channel_id,
            'user_id': user_id,
        }
        topics = [
            t.format(**topics_fields) for t in self.config.get('pubsub_topics')
        ]

        return topics

    async def connect(self):
        """Connect."""
        self.connection = await websockets.connect(
            self.config.get('pubsub_server'),
            ping_interval=self.PING_INTERVAL,
        )
        message = {
            'data': {
                'topics': self.topics,
                'auth_token': self.auth.access_token,
            },
            'nonce': self.nonce,
            'type': 'LISTEN',
        }
        await self.send_message(json.dumps(message))

    async def send_message(self, message: str) -> None:
        """Send a server message.

        Args:
            message (json): JSON data from PubSub.
        """
        await self.connection.send(message)

    async def run(self) -> None:
        """Receive messages from the server."""
        while True:
            try:
                data = json.loads(await self.connection.recv())
                LOG.debug(f'PUBSUB data received: {data}')

            except websockets.exceptions.ConnectionClosedError:
                await self.connect()
                continue

            except Exception as e:
                LOG.error(
                    'PUBSUB error: {}'.format(
                        getattr(e, 'data', repr(e)),
                    )
                )
                traceback.print_exc()
                break

            if data.get('nonce', self.nonce) != self.nonce:
                LOG.debug('PUBSUB data nonce mismatch, discarding.')
                continue

            if data.get('type') == 'PONG':
                data['data'] = {'topic': 'pong'}

            try:
                event = await self.create_event(data)
            except Exception as e:
                LOG.error(
                    'Error creating PUBSUB event: {}'.format(
                        getattr(e, 'message', repr(e)),
                    )
                )
                traceback.print_exc()
                continue

            await EVENT_QUEUE.put(event)

    async def create_event(self, data: json) -> events.Event:
        """Create an event out of the PubSub data.

        Args:
            data (json): JSON data from PubSub.

        Returns:
            event (events.Event): Event object.
        """
        topic = data.get('data', {}).get('topic', '').split('.')[0]

        event_mapping = {
            'automod-queue': pubsub_events.AutoModQueueEvent,
            'channel-bits-events-v2': pubsub_events.BitsEvent,
            'channel-bits-badge-unlocks': pubsub_events.BitsBadgeEvent,
            'channel-points-channel-v1': pubsub_events.ChannelPointsEvent,
            'channel-subscribe-events-v1': pubsub_events.SubscribeEvent,
            'chat_moderator_actions': pubsub_events.ChatModeratorActionsEvent,
            'user-moderation-notifications': pubsub_events.UserModerationEvent,
            'whispers': pubsub_events.WhisperEvent,
            'pong': pubsub_events.PongEvent,
        }

        event = await event_mapping.get(topic, events.DummyEvent)().init(data)

        return event

    async def send_heartbeat(self) -> None:
        """Send the keep-alive PING message.

        This is different from the websocket protocol PING <> PONG.
        """
        while True:
            try:
                await self.send_message(json.dumps({'type': 'PING'}))
                await asyncio.sleep(self.PING_INTERVAL)
            except Exception as e:
                LOG.error(
                    'PUBSUB error: {}'.format(
                        getattr(e, 'message', repr(e)),
                    )
                )
                traceback.print_exc()
                break
