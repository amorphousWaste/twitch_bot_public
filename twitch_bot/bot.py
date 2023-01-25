"""Twitch Bot."""

import asyncio
import re
import sqlite3
import traceback

from datetime import datetime

import api
import auth
import plugin_loader
import utils

from commands import commands
from configs import config_utils
from console import console
from database import database_utils
from emotes import emotes
from events import Event
from init import EVENT_QUEUE
from log import LOG
from moderator import moderator
from obs import obs_utils
from tcp_utils import TCPServer

from chat.chat_connection import ChatConnection
from hotkeys.hotkeys import Hotkeys
from loyalty.loyalty_manager import LoyaltyManager
from obs.obs_connection import OBSConnection

USER_REGEX = re.compile(r'(@[\w]+)')


class TwitchBot(object):
    """Twitch Bot Class."""

    # This id is used for database transactions performed by the bot.
    BOT_USER_ID = 0

    def __init__(self) -> None:
        """Init."""
        super(TwitchBot, self).__init__()

    async def init(
        self,
        authorization: auth.Auth = None,
        chat_connection: ChatConnection = None,
        obs_connection: OBSConnection = None,
        tcp_server: TCPServer = None,
    ) -> object:
        """Async init.

        Args:
            authorization (Auth): Authorization object.
            chat_connection (ChatConnection): Connection object.
                If not given, it will generate one.
            obs_connection (OBSConnection): Connection to OBS.

        Returns:
            (TwitchBot): Bot instance.
        """
        LOG.info('Initializing Bot...')
        await self.startup(
            authorization, chat_connection, obs_connection, tcp_server
        )
        self.console = await console.ConsoleLauncher().init(self)
        LOG.info('Initialization complete.')
        return self

    async def startup(
        self,
        authorization: auth.Auth = None,
        chat_connection: ChatConnection = None,
        obs_connection: OBSConnection = None,
        tcp_server: TCPServer = None,
    ) -> None:
        """Run all the initialization code for the bot.

        Args:
            authorization (Auth): Authorization object.
            chat_connection (ChatConnection): Connection object.
                If not given, it will generate one.
            obs_connection (OBSConnection): Connection to OBS.
            tcp_server (TCPServer): TCP server for external communication.
        """
        await self.reload_config()
        self.auth = authorization or await auth.Auth().init(self.twitch_config)
        self.owner = self.twitch_config.get('owner')
        self.username = self.twitch_config.get('username')
        self.bot_user_data = await api.get_user_data(self.auth, self.username)
        self.bot_user_id = self.bot_user_data.get('id', self.BOT_USER_ID)

        # Initialize the moderator.
        self.moderator = await moderator.Moderator().init(self)

        # Load the text response file.
        self.responses = await config_utils.load_config_file('responses')

        # Create a connection if one does not exist.
        self.connection = (
            chat_connection
            or asyncio.get_event_loop().run_until_complete(
                ChatConnection().init(authorization)
            )
        )

        self.broadcaster_data = await api.get_channel_data(
            self.auth, self.connection.channel.lstrip('#')
        )
        self.broadcaster_id = int(self.broadcaster_data.get('id', 0))

        # Send messages via the connection.
        self.send_message = self.connection.send_message
        self.send_whisper = self.connection.send_whisper

        # Initialize the database connection.
        self.db = await database_utils.Database().init()

        # Load all the plugins.
        await self._initialize_plugins()

        # Get all available emotes.
        self.emotes = await emotes.get_emotes(
            self.auth, self.connection.channel, self.broadcaster_id
        )

        await self.reload_simple_commands()

        # Set up the values for stopping timers when chat is quiet.
        self.stop_on_silence = self.twitch_config.get('stop_on_silence', 0)
        self.last_message_time = datetime.now()

        # Connect to OBS.
        if obs_connection:
            self.obs = await obs_utils.OBS().init(obs_connection)

        # Initialize hotkeys.
        self.hotkey = await Hotkeys().init()

        # Initialize the loyalty manager.
        self.loyalty_manager = await LoyaltyManager().init(self)

        # Initialize TCP server.
        self.tcp_server = tcp_server

        self.running = False

    async def reload_config(self) -> None:
        """Reload the config."""
        # Get the Twitch data from config file.
        self.twitch_config = await config_utils.load_config_file('bot_config')

    async def reload_simple_commands(self) -> None:
        """Reload the simple commands."""
        # Get the simple commands.
        self.simple_commands = await commands.SimpleCommands().init(self)

    async def _initialize_plugins(self, do_reload: bool = False) -> None:
        """Initialize the plugins.

        If a database table does not already exist for the plugin, create one.
        If the table requires a reset, perform that as well.

        Args:
            reload (bool): Used to signal that the plugins should be reloaded.
        """
        self.plugins = await plugin_loader.load_plugins(do_reload)

        for category in self.plugins:
            for command in self.plugins[category]:
                plugin = self.plugins[category][command]
                plugin_name = plugin.__name__
                LOG.debug(f'Initializing {plugin_name}')

                has_table = hasattr(plugin, 'TABLE')
                has_fields = hasattr(plugin, 'FIELDS')

                if has_table and has_fields:
                    # Create a default table for the plugin.
                    await self.db.create_table(plugin_name, None)
                    # Create the custom table with the custom fields.
                    await self.db.create_table(plugin.TABLE, plugin.FIELDS)

                elif not has_table and has_fields:
                    # Create the default table with the custom fields.
                    await self.db.create_table(plugin_name, plugin.FIELDS)

                else:
                    # Create a default table for the plugin.
                    await self.db.create_table(plugin_name, None)

                # Don't reset the tables if reloading the plugins.
                if do_reload:
                    return

                # Reset the given field values in the table.
                if hasattr(plugin, 'RESET'):
                    reset_fields = plugin.RESET
                    reset_fields['last_user_id'] = self.BOT_USER_ID

                    if has_table:
                        # Reset the given fields for the custom table.
                        await self.db.insert(plugin.TABLE, reset_fields)
                    else:
                        # Reset the given fields for the default plugin table.
                        await self.db.insert(plugin_name, reset_fields)

    async def dispatch_command(
        self, event: Event, user: dict, command: str, command_args: list[str]
    ) -> None:
        """Run a command.

        Args:
            event (Event): Server event.
            user (dict): User that sent the message.
                {name: display name, id: user-id}
            command (str): Command string.
            command_args (list): Argument(s) for the command.
        """
        LOG.info(f'Received command: {command}')
        LOG.info(f'Received command_args: {command_args}')

        # Run a simple command if it exists.
        if command in self.simple_commands.commands:
            await self._run_simple_command(event, user, command, command_args)
            return

        # Run the given plugin if it exists.
        plugin = self.plugins.get('command', {}).get(command, None)
        if not plugin:
            LOG.debug(f'Plugin {command} not found.')
            return

        plugin_name = plugin.__name__

        # Check if the user has permission to run the plugin.
        if not await self.moderator.check_plugin_permissions(plugin, user):
            LOG.debug(
                '{} does not have permission to run {}'.format(
                    user['name'], plugin_name
                )
            )
            return

        # Get the last row of the table
        last_row = await self.db.get_last_row(plugin_name)
        if last_row:
            row_dict = dict(last_row)
            last_run = await utils.parse_datetime(row_dict.get('last_run'))
            delta = datetime.now() - last_run
            delta_minutes = delta.seconds / 60

            # Check for a plugin timeout.
            if hasattr(plugin, 'TIMEOUT'):
                if delta_minutes < plugin.TIMEOUT:
                    LOG.debug(
                        f'{plugin_name} cannot be run for '
                        f'{plugin.TIMEOUT - delta_minutes} minutes.'
                    )
                    return

            # Check for user timeout.
            if hasattr(plugin, 'USER_TIMEOUT'):
                if (
                    row_dict.get('last_user_id') == user['id']
                    and delta_minutes < plugin.USER_TIMEOUT
                ):
                    LOG.debug(
                        f'{plugin_name} cannot be run for '
                        f'{plugin.USER_TIMEOUT - delta_minutes} '
                        f'minutes by {user}.'
                    )
                    return

        await self._run_plugin(plugin, event, user, command, command_args)

    async def _run_simple_command(
        self, event: Event, user: dict, command: str, command_args: list[str]
    ) -> None:
        """Attempt to run the plugin.

        Args:
            event (Event): Server event.
            user (dict): User that sent the message.
                {name: display name, id: user-id}
            command (str): Command string.
            command_args (list): Argument(s) for the command.

        Returns:
            None
        """
        simple_command = self.simple_commands.commands[command]
        try:
            await simple_command.run(user, command_args)
        except Exception as e:
            LOG.error(
                'Plugin {} failed: {}'.format(
                    command, getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()

    async def _run_plugin(
        self,
        plugin: object,
        event: Event,
        user: dict,
        command: str,
        command_args: list[str],
    ) -> None:
        """Attempt to run the plugin.

        Args:
            plugin (BasePlugin): Plugin to run.
            event (Event): Server event.
            user (dict): User that sent the message.
                {name: display name, id: user-id}
            command (str): Command string.
            command_args (list): Argument(s) for the command.

        Returns:
            None
        """
        plugin_instance = await plugin().init(
            bot=self,
            event=event,
            user=user,
            command=command,
            command_args=command_args,
        )
        try:
            await plugin_instance._run(self)
        except Exception as e:
            LOG.error(
                'Plugin {} failed: {}'.format(
                    plugin.__name__,
                    getattr(e, 'message', repr(e)),
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()

    async def dispatch_message(
        self, event: Event, user: dict, message: str
    ) -> None:
        """Respond to a message based on the responses config.

        Args:
            event (Event): Server event.
            user (dict): User that sent the message.
                {name: display name, id: user-id}
            message (str): Message string.
        """
        LOG.info(f'Received message: {message}')
        # Filter out any usernames present in the message.
        message = re.sub(USER_REGEX, '', message).strip()

        # Check the message to see if it should trigger a hotkey.
        if await self.hotkey.check(message):
            await self.hotkey.trigger(message)
            return

        # Check the message for any matches in the responses file.
        for phrase in self.responses.get('in', []):
            if phrase.lower() in message.lower():
                await self.send_message(self.responses['in'][phrase])
                return

        for phrase in self.responses.get('is', []):
            if phrase.lower() == message.lower():
                await self.send_message(self.responses['is'][phrase])
                return

        for phrase in self.responses.get('triggers', []):
            if phrase.lower() == message.lower():
                await self._run_plugin(
                    plugin=self.plugins['command'][
                        self.responses['triggers'][phrase]
                    ],
                    event=event,
                    user=user,
                    command=self.responses['triggers'][phrase],
                    command_args=[phrase],
                )
                return

    async def _get_user_db_data(self, user_data: dict) -> sqlite3.Row:
        """Get the user data from the database.

        If the user does not exist, they are added.

        Args:
            user_data (dict): User data from Twitch.

        Returns:
            (sqlite3.Row): Row containing the user data from the database.
        """
        # Get the user data from the databse if it exists.
        user_db_data = await self.db.read(
            'users', queries={'username': user_data['login']}
        )

        # If the user is not in the database, add them.
        if not user_db_data:
            LOG.debug('New user, adding.')
            update_dict = {
                'username': user_data['login'],
                'user_id': user_data['id'],
                'last_join_time': str(datetime.now()),
            }
            await self.db.insert('users', update_dict)

        return await self.db.read(
            'users', queries={'username': user_data['login']}
        )

    async def run(self) -> None:
        """Main functionality of the bot."""
        LOG.info('Running bot loop.')
        while True:
            if EVENT_QUEUE.empty():
                await asyncio.sleep(0.1)
                continue

            LOG.debug('Found an event.')
            event = await EVENT_QUEUE.get()

            try:
                await event.run(self)

            except Exception as e:
                LOG.error(
                    'Event {} failed: {}'.format(
                        event,
                        getattr(e, 'message', repr(e)),
                    )
                )
                # If the level is 'debug', print the traceback as well.
                if LOG.level == 0:
                    traceback.print_exc()
