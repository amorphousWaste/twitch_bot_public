"""Chat Connection."""

import asyncio
import traceback
import websockets

from typing import Callable, Optional

import api
import auth

from configs import config_utils
from exceptions import exceptions
from log import LOG


def ratelimit_decorator(func: Callable) -> Callable:
    """Rate limit messages.

    Args:
        func (function): Function to run.

    Returns:
        decorated (function): The decorated function output.
    """

    async def decorated(message: str, prio: str) -> None:
        """Run the function after a timeout.

        Args:
            message (str): Message to be sent.
            prio (str): The ratelimit priority. The default is USER.
        """
        prio_map = {'BOT': 0.0, 'MOD': 0.01, 'USER': 0.05}
        await asyncio.sleep(prio_map.get('prio', 0.0))
        await func(message, prio)

    return decorated


class ChatConnection(object):
    """ChatConnection."""

    def __init__(self) -> None:
        """Init."""
        super(ChatConnection, self).__init__()

    async def init(
        self,
        authorization: Optional[auth.Auth] = None,
        channel: Optional[str] = None,
    ) -> object:
        """Async init.

        Args:
            authorization (Auth, optional): Auth object.
            channel (str, optional): Channel name.

        Returns:
            self (ChatConnection): Class instance.
        """
        self.twitch_config = await config_utils.load_config_file('bot_config')
        self.auth = authorization or auth.Auth().init(self.twitch_config)
        self.owner = self.twitch_config.get('owner')
        self.username = self.twitch_config.get('username')

        # By default, point the bot at the owner's channel,
        # otherwise the custom channel.
        if not channel:
            self.channel = f'#{self.owner}'
        else:
            self.channel = f'#{channel}'

        # Get the owner's channel data.
        self.channel_data = await api.get_channel_data(
            self.auth, self.twitch_config.get('owner')
        )
        self.channel_id = self.channel_data.get('id')

        LOG.info('Connecting...')
        await self.connect()

        return self

    async def connect(self) -> None:
        """Connect to the IRC chat."""
        await self._connect()

        try:
            await self.authenticate()

        except exceptions.AuthError:
            raise

        # If the connection is reset, try to connect again.
        except ConnectionResetError:
            await self._connect()

        await self.get_capabilities()
        await self.join_chat()
        await self.set_color()

    async def _connect(self) -> None:
        """Perform the connection."""
        self.connected = False

        backoff = 1
        while not self.connected and backoff <= 4:
            try:
                self.socket = await websockets.connect(
                    'wss://{}:{}'.format(
                        self.twitch_config.get('server'),
                        self.twitch_config.get('port'),
                    )
                )
                self.connected = True
                LOG.info('Connected.')

            except Exception as e:
                LOG.error(f'Unable to connect: {e}')
                traceback.print_exc()

                LOG.info(f'Retrying in: {backoff} seconds...')
                await asyncio.sleep(backoff)
                backoff *= 2

        if not self.connected:
            raise exceptions.BotError('Unable to connect to Twitch.')

    async def authenticate(self) -> None:
        """Authenticate the bot."""
        await self.send_server_message(f'PASS oauth:{self.auth.irc_oauth}')
        await self.send_server_message(f'NICK {self.username}')

        response = None
        while not response:
            try:
                response = (
                    (await asyncio.wait_for(self.socket.recv(), timeout=None))
                    .strip('\r\n')
                    .strip()
                )
            except websockets.exceptions.ConnectionClosedError:
                response = None
                await self._connect()

        if 'authentication failed' in response:
            raise exceptions.AuthError('Authentication failed.')

        if 'Login unsuccessful' in response:
            raise exceptions.AuthError('Login unsuccessful.')

    async def get_capabilities(self) -> None:
        """Request the capabilities for the bot."""
        # Get chat command.
        await self.send_server_message('CAP REQ :twitch.tv/commands')
        # Get server joins/parts.
        await self.send_server_message('CAP REQ :twitch.tv/membership')
        # Get message metadata.
        await self.send_server_message('CAP REQ :twitch.tv/tags')

    async def join_chat(self) -> None:
        """Join a chat."""
        await self.send_server_message(f'JOIN {self.channel}')

    async def leave_chat(self) -> None:
        """Leave the chat."""
        await self.send_server_message(f'PART {self.channel}')

    @ratelimit_decorator
    async def send_server_message(
        self, message: str, prio: str = 'USER'
    ) -> None:
        """Send a message to the server.

        Messages are sent via socket and encoded to utf-8 automatically.

        Args:
            message (str): Message to send to the server.
            prio (str): The ratelimit priority. The default is USER.
        """
        data = f'{message}\n'
        LOG.debug(f'Sending message: {data}')
        try:
            await self.socket.send(data)

        # If the pipe breaks, reconnect
        except websockets.exceptions.ConnectionClosedError:
            await self._connect()

    async def send_message(self, message: str) -> None:
        """Publish a message to chat.

        Args:
            message (str): Message to publish.
        """
        await self.send_server_message(f'PRIVMSG {self.channel} :{message}')

    async def send_command(self, command: str) -> None:
        """Send a command to chat.

        Args:
            command (str): Message to publish.
        """
        await self.send_message(f'/{command}')

    async def send_whisper(self, user: dict[str:int], message: str) -> None:
        """Publish a whisper to chat.

        This does not seem to work for unverified bots.

        Args:
            user (dict): User that sent the message.
                {name: display name, id: user-id}
            message (str): Message to publish.
        """
        await self.send_message('/w {} {}'.format(user.lower(), message))

    async def set_color(self, color: Optional[str] = 'CadetBlue') -> None:
        """Set the bot color in chat.

        Only 'Turbo' users can specify custom hex colors, otherwise one of the
        standard chat colors can be used:
            Blue, BlueViolet, CadetBlue, Chocolate, Coral, DodgerBlue,
            Firebrick, GoldenRod, Green, HotPink, OrangeRed, Red, SeaGreen,
            SpringGreen, YellowGreen

        Args:
            color (str, optional): A standard color name or hex color.
                hex colors need a leading #.
                Example: #408CFF
        """
        await self.send_command(f'color {color}')
