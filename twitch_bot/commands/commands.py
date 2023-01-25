"""Simple Commands."""

import json
import os
import re
import traceback

from random import randint

import api
import chatters
import utils

from log import LOG


COMMANDS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'commands', 'commands.json'
)

RANDOM_PATTERN = re.compile(r'rand(?P<start>\d+)-(?P<end>\d+)')
VARS_PATTERN = re.compile(r'{([^}]*)}')


class SimpleCommands(object):
    """Simple commands."""

    def __init__(self) -> None:
        """Init."""
        super(SimpleCommands, self).__init__()

    async def init(self, bot: object) -> object:
        """Async init.

        Args:
            bot (TwitchBot): Bot instance.
        """
        self.bot = bot
        self.commands = await self.load_commands()
        return self

    async def load_commands(self) -> dict:
        """Load the commands file.

        Returns:
            (dict): Commands as a dictionary.
        """
        with open(COMMANDS_FILE, 'r') as in_file:
            command_data = json.load(in_file)

        commands = {}
        for item in command_data.keys():
            commands[item] = await Command().init(
                self.bot, item, command_data[item]
            )

        return commands

    async def write_commands(self) -> None:
        """Write the commands to the commands file."""
        data = {}
        for command in self.commands:
            data[command] = self.commands[command].code

        with open(COMMANDS_FILE, 'w') as out_file:
            json.dump(data, out_file)

    async def add_command(self, name: str, code: str) -> None:
        """Add a simple command.

        Args:
            name (str): Name of the command.
            code (str): Code for the command.

        Returns:
            (bool): True if successful, False otherwise.
        """
        try:
            if name not in self.commands.keys():
                self.commands[name] = await Command().init(
                    self.bot, name, code
                )
                await self.write_commands()
                return True

        except Exception as e:
            LOG.error(
                'Unable to add {} command: {}'.format(
                    name, getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()

        return False

    async def edit_command(self, name: str, code: str) -> None:
        """Edit a simple command.

        Args:
            name (str): Name of the command.
            code (str): Code for the command.

        Returns:
            (bool): True if successful, False otherwise.
        """
        try:
            if name in self.commands.keys():
                self.commands[name].code = code
                await self.write_commands()
                return True

        except Exception as e:
            LOG.error(
                'Unable to edit {} command: {}'.format(
                    name, getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()

        return False

    async def delete_command(self, name: str, code: str) -> None:
        """Delete a simple command.

        Args:
            name (str): Name of the command.
            code (str): Code for the command.
        """
        try:
            if name in self.commands.keys():
                del self.commands[name]
                await self.write_commands()
                return True

        except Exception as e:
            LOG.error(
                'Unable to delete {} command: {}'.format(
                    name, getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()

        return False


class Command(object):
    """Command."""

    def __init__(self) -> None:
        """Init."""
        super(Command, self).__init__()

    async def init(self, bot: object, name: str, code: str) -> object:
        """Async init."""
        self.bot = bot
        self.name = name
        self.code = code

        return self

    async def run(self, user: dict, args: list[str]) -> None:
        """Run the command.

        Args:
            user (dict): User that sent the message.
                {name: display name, id: user-id}
            args (list): Argument(s) for the command.
        """
        self.user = user
        self.args = args or ['']
        response = await self.parse_vars()
        await self.bot.send_message(response)

    async def parse_vars(self) -> str:  # noqa
        """Parse the variables in the code string.

        Returns:
            (str): Code with the variables replaced with data.
        """
        self.variables = re.findall(VARS_PATTERN, self.code)

        variable_map = {}

        self.chatters = await chatters.Chatters().init(
            self.bot.connection.channel.lstrip('#')
        )

        if 'chatters' in self.variables:
            variable_map['chatters'] = self.chatters.chatter_count

        if 'followers' in self.variables:
            variable_map['followers'] = await self.get_follower_count()

        if 'randtgt' in self.variables:
            variable_map['randtgt'] = await self.get_random_chatter()

        if 'subscribers' in self.variables:
            variable_map['subscribers'] = await self.get_subscriber_count()

        if 'target' in self.variables:
            variable_map['target'] = self.args[0]

        if 'uptime' in self.variables:
            variable_map['uptime'] = await utils.get_uptime(self.bot)

        if 'user' in self.variables:
            variable_map['user'] = self.user.get('name')

        if 'views' in self.variables:
            variable_map['views'] = await self.get_view_count()

        for variable in self.variables:
            match = re.findall(RANDOM_PATTERN, variable)
            if match:
                variable_map[variable] = await self.get_random_number()

        return self.code.format(**variable_map)

    async def get_random_chatter(self) -> str:
        """Pick a random chatter.

        Returns:
            (str): Random chatter name.
        """
        return self.chatters.chatters[
            randint(0, self.chatters.chatter_count - 1)
        ]

    async def get_follower_count(self) -> int:
        """Get the total number of followers.

        Returns:
            (int): Follower count.
        """
        response = await api.get_follow_count(
            self.bot.auth, self.bot.connection.channel_id
        )
        return response

    async def get_random_number(self) -> str:
        """Generate a random number between the given values.

        Returns:
            (str): Random value.
        """
        random_variables = re.findall(RANDOM_PATTERN, self.code)
        if not random_variables:
            return 0

        return randint(
            int(random_variables[0][0]), int(random_variables[0][1])
        )

    async def get_view_count(self) -> int:
        """Get view count.

        Return:
            (int): View count.
        """
        user_data = await api.get_user_data(
            self.bot.auth, self.bot.connection.channel.lstrip('#')
        )
        return user_data.get('view_count')

    async def get_subscriber_count(self) -> int:
        """Get subscribers.

        Return:
            (int): Subscriber count.
        """
        return len(await api.get_subscribers(self.bot.auth))
