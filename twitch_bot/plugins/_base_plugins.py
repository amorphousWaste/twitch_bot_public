"""Base plugin classes."""

from database import database_utils


class BasePlugin(object):
    """Base plugin class."""

    # Replace with the actual command string
    # (Do not include the '!')
    COMMAND = 'command_string'

    def __init__(self):
        """Init."""
        super(BasePlugin, self).__init__()

    async def init(
        self,
        bot: object,
        event: object,
        user: dict,
        command: str,
        command_args: list[str],
    ) -> object:
        """Async init.

        Args:
            bot (TwitchBot): The bot instance running the plugin.
            event (event): Server event.
            user (dict): User that sent the message.
                {name: display name, id: user-id}
            command (str): Command string.
            command_args (list): Argument(s) for the command.
            last_row (tuple): Data from the last row in the table.

        Returns:
            self (BasePlugin): The plugin instance.
        """
        self.bot = bot
        self.event = event
        self.user = user
        self.command = command
        self.command_args = command_args

        self.db = bot.db
        self.send_message = self.bot.connection.send_message

        return self

    @database_utils.database_decorator
    async def _run(self, last_row: object) -> None:
        """Run wrapper.

        Args:
            last_row (tuple): Data from the last row in the table.

        Returns:
            (None|dict|int): Return from the plugin run() function.
        """
        self.last_row = last_row
        return await self.run()

    async def run(self):
        """The main code of the plugin."""
        raise NotImplementedError(
            'You need to create your own run() function for your plugin.'
        )


class BaseCommandPlugin(BasePlugin):
    """Base command plugin class.

    Used for any plugins you want to run from chat.
    Commands take the form '!command'.
    """

    # Replace with the actual command string
    # (Do not include the '!')
    COMMAND = 'command_string'


class BaseIntervalPlugin(BasePlugin):
    """Base class for interval plugins.

    Used for any plugins you want to run automatically on an interval
    or from chat. It is essentially the same as a normal command with the
    extra INTERVAL attribute.
    Commands take the form '!command'.
    """

    # Replace with the actual command string
    # (Do not include the '!')
    KEYWORD = 'command_string'
    # This is the interval in minutes.
    INTERVAL = 5


class BaseRedemptionPlugin(BasePlugin):
    """Base class for redemption plugins.

    Used for any plugins you want to run based on a channel point redemption.
    These plugins are triggered from the RewardRedemptionEvent.
    """

    # Replace with the actual redemption string
    KEYWORD = 'command_string'
