"""Websocket server."""

import asyncio
import base64
import hashlib
import json
import time
import websockets

import auth

from typing import Callable

from configs import config_utils
from exceptions import exceptions
from log import LOG
from obs import obs_base_classes, obs_event_manager, obs_events


class OBSConnection(object):
    """OBS connection class."""

    def __init__(self):
        """Init."""
        super(OBSConnection, self).__init__()

    async def init(self, authorization: auth.Auth = None) -> object:
        """Async init.

        Args:
            authorization (Auth): Authorization object.

        Returns:
            self (OBSConnection): Class instance.
        """
        self.twitch_config = await config_utils.load_config_file('bot_config')
        self.auth = authorization or await auth.Auth().init(self.twitch_config)

        self.host = self.twitch_config['obs_host']
        self.port = self.twitch_config['obs_port']
        self.password = self.auth.obs_password

        self.connected = False
        self.eventmanager = (
            await obs_event_manager.CallbackEventManager().init()
        )
        self.message_id = 1
        self.answers = {}

        return self

    def message_wrapper(func: Callable) -> None:
        """Decorator to check the connection to OBS.

        Args:
            func (Callable): Decorated function.

        Returns:
            (Any): Result of the decorated function.
        """

        async def wrapper(self, data: dict) -> None:
            """Wrapped function.

            Args:
                data (dict): Data to send.

            Returns:
                result (dict) from the server.
            """
            await func(self, data)
            result = await self.await_response(self.message_id)
            self.message_id += 1

            return result

        return wrapper

    async def connect(self) -> None:
        """Connect to the websocket server."""
        if self.connected:
            return

        reconnect_time = 5
        LOG.info('Connecting...')
        while not self.connected:
            try:
                self.connection = await websockets.connect(
                    f'ws://{self.host}:{self.port}'
                )
                await self.authorize()
                self.connected = True

            except (websockets.WebSocketException, OSError) as e:
                LOG.error(f'An error occured while trying to connect: {e}')
                LOG.error(
                    f'Re-attempting connection in {reconnect_time} seconds.'
                )
                await asyncio.sleep(reconnect_time)

            except Exception as e:
                LOG.error(f'A connection error occured: {e}\nReconnecting...')
                await asyncio.sleep(reconnect_time)

        LOG.info('Connected.')

    async def reconnect(self) -> None:
        """Restart the connection to the websocket server."""
        LOG.info('Attempting reconnection...')
        try:
            await self.disconnect()
        except Exception as e:
            LOG.error(f'An error occured disconnecting: {e}')

        await self.connect()

    async def disconnect(self) -> None:
        """Disconnect from websocket server."""
        LOG.info('Disconnecting...')
        try:
            await self.connection.close()
        except Exception as e:
            LOG.error(f'An error occured; closing the connection: {e}')

        self.connected = False
        LOG.info('Disconnected.')

    async def authorize(self) -> None:
        """Authorize the connection."""
        auth_payload = {
            'request-type': 'GetAuthRequired',
            'message-id': str(self.message_id),
        }
        await self.connection.send(json.dumps(auth_payload))
        result = json.loads(await self.connection.recv())

        if result['status'] != 'ok':
            raise exceptions.OBSError(result['error'])

        if result.get('authRequired'):
            secret = base64.b64encode(
                hashlib.sha256(
                    (self.password + result['salt']).encode('utf-8')
                ).digest()
            )
            auth = base64.b64encode(
                hashlib.sha256(
                    secret + result['challenge'].encode('utf-8')
                ).digest()
            ).decode('utf-8')

            auth_payload = {
                'request-type': 'Authenticate',
                'message-id': str(self.message_id),
                'auth': auth,
            }

            await self.connection.send(json.dumps(auth_payload))
            result = json.loads(await self.connection.recv())
            if result['status'] != 'ok':
                raise exceptions.OBSError(result['error'])

    async def call(self, request: object) -> object:
        """Make a call to the OBS server.

        Args:
            request (object): Request to send to the server.

        Returns:
            request (object): Request with response data.
        """
        if not isinstance(request, obs_base_classes.BaseRequests):
            raise exceptions.OBSError(f'{request} is not a valid request.')

        payload = await request.data()
        response = await self.send(payload)
        await request.input(response)

        return request

    @message_wrapper
    async def send(self, data: dict) -> None:
        """Make a raw json call to the OBS server through the Websocket.

        Args:
            data (dict): Data to send.
        """
        data['message-id'] = str(self.message_id)
        LOG.debug(f'Sending message {self.message_id}: {data}')
        await self.connection.send(json.dumps(data))

    async def await_response(self, message_id: int) -> dict:
        LOG.debug('Waiting for reply...')
        timeout = time.time() + 60  # Timeout = 60s
        while time.time() < timeout:
            LOG.debug(f'{message_id} <-> {self.answers}')
            if message_id in self.answers:
                return self.answers.pop(message_id)

            await asyncio.sleep(0.1)

        raise exceptions.OBSError(f'No answer for message {message_id}')

    async def register(self, func: Callable, event: object = None) -> None:
        """Register a new callback.

        Args:
            func (Callable): Callback function to run on event.
            event (Event): Event to trigger.
                Default is None, which will trigger on all events.
        """
        await self.eventmanager.register(func, event)

    async def unregister(self, func: Callable, event: object = None) -> None:
        """Unregister an existing callback.

        Args:
            func (Callable): Callback function to run on event.
            event (Event): Event to trigger.
                Default is None, which would have triggered on all events.
        """
        await self.eventmanager.unregister(func, event)

    async def process_message(self, message: json) -> None:
        """Process the received message.

        Args:
            message (json): JSON message received from OBS.
        """
        if not message:
            LOG.debug('Blank message; skipping.')
            return

        result = json.loads(message)
        if 'update-type' in result:
            event = await self.build_event(result)
            await self.eventmanager.trigger(event)

        elif 'message-id' in result:
            LOG.debug(f'Got answer for id {result["message-id"]}: {result}')
            self.answers[int(result['message-id'])] = result

        else:
            LOG.warning(f'Unknown message: {result}')

    async def build_event(self, data: dict) -> object:
        """Build an event from a received message.

        Args:
            data (dict): Message data.

        Returns:
            obj (object): Event.
        """
        name = data['update-type']
        LOG.debug(f'Building event: {name}')
        try:
            call = await getattr(obs_events, name)().init()

        except AttributeError:
            raise exceptions.OBSError(f'Invalid event {name}')

        await call.input(data)
        return call

    async def run(self) -> None:  # noqa
        """Run the receiver."""
        await self.connect()
        self.running = True
        LOG.debug('Running receiver loop.')

        while self.running:
            try:
                message = await self.connection.recv()
                LOG.debug(f'Received message: {message}')

                await self.process_message(message)

            except (
                websockets.exceptions.ConnectionClosedOK,
                websockets.ConnectionClosedError,
            ):
                if self.running:
                    LOG.warning('OBS server has gone offline.')
                    # self.running = False
                    await self.reconnect()

            except OSError:
                if self.running:
                    LOG.warning('Cannot connect to OBS server.')
                    # self.running = False
                    await self.reconnect()

            except (ValueError, exceptions.OBSError) as e:
                LOG.warning(f'Invalid message: {message} ({e})')

            message = ''

        LOG.debug('Receiver loop no longer running.')
