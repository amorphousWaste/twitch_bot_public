"""Chat Message Event."""

import re

from datetime import datetime

import api

from events import Event
from init import CACHE
from log import LOG

MESSAGE_RE = re.compile(
    r'(@(?P<metadata>.*)\s)?\:(?P<username>\w*)?\!?(?P<address>\w*\@?\w*\.?'
    r'tmi\.twitch\.tv)\s(?P<type>\w+)\s\#?(?P<channel>[\w\*]+)\s?\:?'
    r'(?P<message>.+)?'
)


async def get_event_type(data: dict) -> str:
    """Get the event type from the event data.

    Args:
        data (str): Data from the server.

    Returns:
        (str): Event type.
    """
    matches = re.match(MESSAGE_RE, data)
    match_dict = matches.groupdict() if matches else {}
    return match_dict.get('type', '')


class ChatEvent(Event):
    """Message event.

    This object breakes down a server message into its parts and makes it
    easier to access the individual elements.

    Do not use this class directly, only subclass from it.
    """

    def __init__(self) -> None:
        """Init."""
        super(ChatEvent, self).__init__()

    async def init(self, data: str):
        """Async init.

        Args:
            data (str): Data from the server.
        """
        self.data = data
        if not self.data:
            LOG.warning('Event has no data.')
            return

        # Attempt to break down the message into parts.
        matches = re.match(MESSAGE_RE, self.data)
        match_dict = matches.groupdict() if matches else {}

        # Metadata from the server data.
        metadata = match_dict.get('metadata')
        data_dict = {}
        if metadata:
            for datum in metadata.split(';'):
                key, value = datum.split('=')
                data_dict[key] = value

        self.badge_info = data_dict.get('badge-info', '')
        self.badges = data_dict.get('badges', '')
        self.client_nonce = data_dict.get('client-nonce', '')
        self.color = data_dict.get('color', '')
        self.display_name = data_dict.get('display-name', '')
        self.emotes = data_dict.get('emotes', '')
        self.flags = data_dict.get('flags', '')
        self.id = data_dict.get('id', '')
        self.mod = False if int(data_dict.get('mod', 0)) == 0 else True
        self.room_id = int(data_dict.get('room-id', 0))
        self.subscriber = False if int(data_dict.get('mod', 0)) == 0 else True
        self.tmi_sent_ts = int(data_dict.get('tmi-sent-ts', 0))
        self.turbo = False if int(data_dict.get('mod', 0)) == 0 else True
        self.user_id = int(data_dict.get('user-id', 0))
        self.user_type = data_dict.get('user-type', '')

        # Event data from the server message.
        self.username = match_dict.get('username', '')
        self.address = match_dict.get('address', '')
        self.type = match_dict.get('type', '')
        self.channel = match_dict.get('channel', '')
        self.message = match_dict.get('message', '')

        return

    def __dict__(self) -> dict:
        """Return the object as a dictionary."""
        return {
            'badge_info': self.badge_info,
            'badges': self.badges,
            'client_nonce': self.client_nonce,
            'color': self.color,
            'display_name': self.display_name,
            'emotes': self.emotes,
            'flags': self.flags,
            'id': self.id,
            'mod': self.mod,
            'room_id': self.room_id,
            'subscriber': self.subscriber,
            'tmi_sent_ts': self.tmi_sent_ts,
            'turbo': self.turbo,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'username': self.username,
            'address': self.address,
            'type': self.type,
            'channel': self.channel,
            'message': self.message,
        }

    def __str__(self) -> str:
        """Return the object as a str."""
        return str(self.__dict__())


class ExistingUsersEvent(ChatEvent):
    """Run when a list of existing users in chat is received."""

    def __init__(self) -> None:
        """Init."""
        super(ExistingUsersEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(ExistingUsersEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A name list was received: {self}.')
        raw_username_list = self.message.split(':')
        if not raw_username_list or len(raw_username_list) < 2:
            return

        username_list = [
            u
            for u in raw_username_list[1].split()
            if u not in [bot.owner, bot.username]
        ]

        for username in username_list:
            # Get the user data from the username.
            user_data = await api.get_user_data(bot.auth, username)
            LOG.debug(f'user_data: {user_data}')
            if not user_data:
                return

            # Get the user data from the database.
            user_db_data = await bot._get_user_db_data(user_data)

            # Otherwise, update the user data in the database.
            update_dict = {'last_join_time': str(datetime.now())}
            await bot.db.update(
                'users', update_dict, {'username': user_db_data['username']}
            )

            # Add user to cache.
            user_cache = await CACHE.get('users')
            if username not in user_cache.data:
                user_cache.data.append(username)


class NamesEndEvent(ChatEvent):
    """Run when the event signals the end of the NAMES list."""

    def __init__(self) -> None:
        """Init."""
        super(NamesEndEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(NamesEndEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A NamesEndEvent was received: {self}.')


class AckEvent(ChatEvent):
    """Run when the event signals a command acknowledgement."""

    def __init__(self) -> None:
        """Init."""
        super(AckEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(AckEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'An AckEvent was received: {self}.')


class CapEvent(ChatEvent):
    """Run when the event signals a capability."""

    def __init__(self) -> None:
        """Init."""
        super(CapEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(CapEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        if 'ACK' in self.message:
            ack = await AckEvent().init(self.data)
            await ack.run(bot)
        else:
            LOG.debug(f'A CapEvent was received: {self}.')


class JoinEvent(ChatEvent):
    """Join event.

    This is called any time a user joins the chat.
    """

    def __init__(self) -> None:
        """Init."""
        super(JoinEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(JoinEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        # Get the username from the event.
        username = self.username
        LOG.info(f'{username} joined.')

        # Get the user data from the username.
        user_data = await api.get_user_data(bot.auth, username)
        LOG.debug(f'user_data: {user_data}')
        if not user_data:
            return

        # Get the user data from the database.
        user_db_data = await bot._get_user_db_data(user_data)

        # Otherwise, update the user data in the database.
        update_dict = {'last_join_time': str(datetime.now())}
        await bot.db.update(
            'users', update_dict, {'username': user_db_data['username']}
        )

        # Announce the user if 'announce' is set in the database.
        if user_db_data['announce'] == 1:
            await bot.send_message(f'Welcome {username}!')

        # Add user to cache.
        user_cache = await CACHE.get('users')
        if username not in user_cache.data:
            user_cache.data.append(username)


class NoticeEvent(ChatEvent):
    """Run when a notice event is received."""

    def __init__(self) -> None:
        """Init."""
        super(NoticeEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(NoticeEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A NoticeEvent was received: {self}.')


class PartEvent(ChatEvent):
    """Part event.

    This is called any time a user leaves the chat.
    """

    def __init__(self) -> None:
        """Init."""
        super(PartEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(PartEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        # Get the username from the event.
        username = self.username
        LOG.info(f'{username} left.')

        # Get the user data from the username.
        user_data = await api.get_user_data(bot.auth, username)
        LOG.debug(f'user_data: {user_data}')
        if not user_data:
            return

        # Get the user data from the database.
        user_db_data = await bot._get_user_db_data(user_data)

        # Update the time spent watching the stream.
        last_leave_time = datetime.now()
        session_time_watched = (
            last_leave_time
            - datetime.fromisoformat(user_db_data['last_join_time'])
        ).total_seconds() / 60
        time_watched = int(user_db_data['time_watched'] + session_time_watched)

        update_dict = {
            'time_watched': time_watched,
            'last_leave_time': last_leave_time,
            'messages_sent_session': 0,
            'messages_sent_total': (
                int(user_db_data['messages_sent_total'])
                + int(user_db_data['messages_sent_session'])
            ),
        }

        # Update the database.
        await bot.db.update(
            'users', update_dict, {'user_id': user_db_data['user_id']}
        )

        # Remove user from cache.
        user_cache = await CACHE.get('users')
        if username in user_cache.data:
            user_cache.data.remove(username)


class PubmsgEvent(ChatEvent):
    """Receive a message event.

    This is called any time a message is published in the chat.
    """

    def __init__(self) -> None:
        """Init."""
        super(PubmsgEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(PubmsgEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        # Parse the event.
        user = {'name': self.username, 'id': self.user_id}
        message = self.message
        LOG.info(f'Message from {user["name"]}: {message}')

        bot.last_message_time = datetime.now()

        # Get the user data from the username.
        user_data = await api.get_user_data(bot.auth, user['name'])
        LOG.debug(f'user_data: {user_data}')
        if not user_data:
            return

        # Get the user data from the database.
        user_db_data = await bot._get_user_db_data(user_data)

        # Run the message past the Moderator.
        mod_approved = await bot.moderator.check_message(user, message)
        if not mod_approved:
            LOG.debug('Message rejected.')
            return

        # If a chat message starts with an exclamation point,
        # try to run it as a command.
        if message.startswith('!'):
            split_message = message.split(' ', maxsplit=1)
            command = split_message[0].lstrip('!')

            if len(split_message) >= 2:
                command_args = split_message[1].split(' ')
            else:
                command_args = None

            await bot.dispatch_command(self, user, command, command_args)

        # If the message doesn't start with a command, send the message to the
        # text parser.
        else:
            await bot.dispatch_message(self, user, message)

        # Welcome first time chatters.
        if user_db_data['messages_sent_total'] == 0:
            LOG.debug('First time chatter.')
            await bot.send_message(f'Welcome @{self.username}!')

        # Increment the number of sent messages in the database.
        users_update_dict = {
            'messages_sent_session': user_db_data['messages_sent_session'] + 1
        }

        await bot.db.update(
            'users', users_update_dict, {'user_id': user_db_data['user_id']}
        )

        # Update the stream stats database.
        stream_stats_last_row = dict(await bot.db.get_last_row('stream_stats'))

        await bot.db.update(
            'stream_stats',
            {'messages': int(stream_stats_last_row.get('messages', 0)) + 1},
            {'id': stream_stats_last_row.get('id', 0)},
        )

        # Add unique chatters to the cache.
        chatters_cache = await CACHE.get('chatters')
        if self.username not in chatters_cache.data:
            chatters_cache.data.append(self.username)


class RoomstateEvent(ChatEvent):
    """Run when the event signals the room state."""

    def __init__(self) -> None:
        """Init."""
        super(RoomstateEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(RoomstateEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A RoomstateEvent was received: {self}.')


class UsernoticeEvent(ChatEvent):
    """Run when the event signals a user notice."""

    def __init__(self) -> None:
        """Init."""
        super(UsernoticeEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(UsernoticeEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A UsernoticeEvent was received: {self}.')


class UserstateEvent(ChatEvent):
    """Run when the event signals the user state."""

    def __init__(self) -> None:
        """Init."""
        super(UserstateEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(UserstateEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A UserstateEvent was received: {self}.')


class WhisperEvent(ChatEvent):
    """Run when the bot receives a whisper."""

    def __init__(self) -> None:
        """Init."""
        super(WhisperEvent, self).__init__()

    async def init(self, data: str) -> object:
        """Async init.

        Args:
            data (str): Data from the server.
        """
        await super(WhisperEvent, self).init(data)
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A WhisperEvent was received: {self}.')
