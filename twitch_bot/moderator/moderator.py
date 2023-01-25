"""Moderator."""

from configs import config_utils

from datetime import datetime
from typing import Callable

from log import LOG

URL_REGEX = r'[a-zA-Z0-9@:%_\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}'


class Moderator(object):
    """Twitch Bot Moderator."""

    def __init__(self) -> None:
        """Init."""

        super(Moderator, self).__init__()

    async def init(self, bot: object) -> object:
        """Async init.

        Args:
            bot (TwitchBot): The running Twitch Bot.
        """
        self.bot = bot
        self.config = await config_utils.load_config_file('moderator_config')
        return self

    async def check_message(self, user: dict, message: str) -> bool:
        """Check the message for banned terms.

        Args:
            user (dict): Dictionary containing the message sender data.
            message (str): Sent message.

        Returns:
            (bool): True if the message is approved, False otherwise.
        """
        banned_terms = self.config.get('banned_terms', [])
        if not banned_terms:
            return True

        for term in banned_terms:
            if message.find(term) >= 1:
                self.set_timeout(user)
                return False

        return True

    async def check_plugin_permissions(
        self, plugin: Callable, user: dict
    ) -> bool:
        """Confirm the given user has permissions to run the given plugin.

        Args:
            plugin (BaseCommandPlugin): Plugin class.
            user (dict): Dictionary containing the message sender data.

        Returns:
            (bool): True if the user has permissions, False otherwise.
        """
        # Allow the plugin to run for all users if there are no restrictions.
        if not hasattr(plugin, 'ALLOWED'):
            LOG.debug('No restrictions, allowing.')
            return True

        # Always allow the owner to run plugins.
        if user['name'].lower() == self.bot.owner.lower():
            LOG.debug('Run by owner, allowing.')
            return True

        if 'bot' in plugin.ALLOWED:
            LOG.debug('Only the owner or bot can run this.')
            return False

        if 'safelist' in plugin.ALLOWED:
            LOG.debug('Only the safelisted users can run this.')
            safelisted_users = self.bot.twitch_config.get('safelist')
            if user['name'] in safelisted_users:
                return True

        # Get the user data from the database.
        user_db_data = await self.bot.db.read(
            'users', queries={'user_id': user['id']}
        )
        is_mod = user_db_data['is_mod']
        is_regular = user_db_data['is_regular']

        # If the plugin requires a mod and the user is a mod,
        # allow the plugin to be run.
        if 'mod' in plugin.ALLOWED and is_mod == 1:
            LOG.debug('Run by mod, allowing.')
            return True

        # If the plugin requires a regular and the user is a mod or regular,
        # allow the plugin to be run.
        if 'regular' in plugin.ALLOWED and (is_mod == 1 or is_regular == 1):
            LOG.debug('Run by regular, allowing.')
            return True

        # Deny running the plugin to anyone who did not meet any requirements.
        return False

    async def check_cooldowns(self, plugin: Callable, user: dict) -> bool:
        """Confirm the given user has permissions to run the given plugin.

        Args:
            plugin (BaseCommandPlugin): Plugin class.
            user (dict): Dictionary containing the message sender data.

        Returns:
            (bool): True if the user has permissions, False otherwise.
        """
        # Check if the plugin has a custom table, otherwise use the default.
        if hasattr(plugin, 'TABLE'):
            table = plugin.TABLE
        else:
            table = plugin.__class__.__name__

        # Check for the 'GLOBAL_COOLDOWN' attribute and get its value
        # if it exists.
        if hasattr(plugin, 'GLOBAL_COOLDOWN'):
            cooldown = plugin.GLOBAL_COOLDOWN
            db_data = await self.bot.db.read(table, columns=['last_run'])

        # Check for the 'USER_COOLDOWN' attribute and get its value
        # if it exists.
        elif hasattr(plugin, 'USER_COOLDOWN'):
            cooldown = plugin.USER_COOLDOWN
            db_data = await self.bot.db.read(
                table, columns=['last_run'], queries={'username': user['name']}
            )

        # If neither, then allow it to run.
        else:
            return True

        # Compare the current time to the last run time and see if it is
        # longer than the cooldown.
        last_run = datetime.fromisoformat(db_data['last_run'])
        elapsed = datetime.now() - last_run
        if elapsed.seconds / 60 > cooldown:
            return True
        else:
            return False

    async def set_timeout(self, user: dict):
        """Set a timeout for the user for violating moderator rules.

        Args:
            user (dict): Dictionary containing the message sender data.
        """
        raise NotImplementedError()

    async def check_timeout(self, user: dict) -> bool:
        """Check the user for a timeout.

        Args:
            user (dict): Dictionary containing the message sender data.

        Returns:
            (bool): True if the user is timed out, False otherwise.
        """
        raise NotImplementedError()

    async def ban_user(self, user: dict) -> None:
        """Ban a user.

        Args:
            user (dict): Dictionary containing the message sender data.
        """
        raise NotImplementedError()

    async def delete_message(self, event: object) -> None:
        """Delete a message based on the message ID.

        Args:
            event (object): ChatEvent object.
        """
        self.bot.connection.send_command(f'delete {event.id}')
