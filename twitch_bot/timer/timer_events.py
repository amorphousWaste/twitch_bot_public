"""Timer Events."""

from datetime import datetime

from events import Event
from log import LOG


class TimerEvent(Event):
    """Timer event."""

    def __init__(self) -> None:
        """Init."""
        super(TimerEvent, self).__init__()

    async def init(self, interval: int) -> object:
        """Async init.

        Args:
            interval (int): Timer interval.
        """
        self.interval = interval

        return self

    async def run(self, bot: object) -> None:
        """Run when a timer event is sent.

        This is used to trigger plugins that run on an interval.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A timer event was received: {self}.')
        interval_plugins = bot.plugins.get('interval', {})
        user = {'name': 'bot', 'id': 0}

        # If stop on silence is enabled, check when the last message was sent
        # and don't trigger the timed plugins if it has been longer than the
        # configured time.
        time_since_last = (datetime.now() - bot.last_message_time).seconds / 60

        bypass_silence_list = bot.twitch_config.get('bypass_silence_list', [])

        if bot.stop_on_silence > 0 and time_since_last >= bot.stop_on_silence:
            LOG.info('Ignoring timers, chat is quiet.')
            silent = True
        else:
            silent = False

        for plugin_command in interval_plugins:
            plugin = interval_plugins[plugin_command]
            plugin_name = plugin.__name__

            if silent and plugin_name not in bypass_silence_list:
                continue

            last_row = await bot.db.get_last_row(plugin_name)
            if not last_row:
                await bot._run_plugin(plugin, self, user, '', '')
                continue

            row_dict = dict(last_row)
            try:
                last_run = datetime.strptime(
                    row_dict.get('last_run'), '%Y-%m-%d %H:%M:%S'
                )
            except ValueError:
                last_run = datetime.strptime(
                    row_dict.get('last_run'), '%Y-%m-%d %H:%M:%S.%f'
                )

            delta = datetime.now() - last_run
            delta_minutes = int(delta.seconds / 60)
            LOG.debug(f'delta_minutes: {delta_minutes}')

            if delta_minutes > plugin.INTERVAL:
                await bot._run_plugin(plugin, self, user, '', '')

    def __dict__(self) -> dict:
        """Return the object as a dictionary."""
        return {'interval': self.interval}

    def __str__(self) -> str:
        """Return the object as a str."""
        return str(self.__dict__())
