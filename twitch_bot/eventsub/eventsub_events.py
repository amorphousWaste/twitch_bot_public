"""EventSub Events."""

from datetime import datetime

import api
import utils

from chat.chat_events import PartEvent
from discord import discord_sender
from events import Event
from init import CACHE
from log import LOG


class EventSubEvent(Event):
    """EventSub event."""

    def __init__(self) -> None:
        """Init."""
        super(EventSubEvent, self).__init__()


class ChannelUpdate(EventSubEvent):
    """Channel update event."""

    def __init__(self) -> None:
        """Init."""
        super(ChannelUpdate, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.title = self.event.get('title', '')
        self.language = self.event.get('language', '')
        self.category_id = int(self.event.get('category_id', 0))
        self.category_name = self.event.get('category_name', '')
        self.is_mature = self.event.get('is_mature', False)

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A ChannelUpdate was received: {self}')
        await bot.send_message('Stream info updated.')


class FollowEvent(EventSubEvent):
    """Follow event."""

    def __init__(self) -> None:
        """Init."""
        super(FollowEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.user_id = int(self.event.get('user_id', 0))
        self.user_login = self.event.get('user_login', '')
        self.user_name = self.event.get('user_name', '')
        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.followed_at = await utils.parse_datetime(
            self.event.get('followed_at', '')
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A FollowEvent was received: {self}')
        await bot.send_message(
            f'Welcome {self.user_name}, thank you for following!'
        )

        # Update the stream stats table.
        last_row = dict(await bot.db.get_last_row('stream_stats'))
        await bot.db.update(
            'stream_stats',
            {'followers': last_row['followers'] + 1},
            {'id': last_row['id']},
        )

        await bot.loyalty_manager.add_loyalty_points_for_event(
            self.user_name, 'follow'
        )


class SubscribeEvent(EventSubEvent):
    """Subscribe event."""

    def __init__(self) -> None:
        """Init."""
        super(SubscribeEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.user_id = int(self.event.get('user_id', 0))
        self.user_login = self.event.get('user_login', '')
        self.user_name = self.event.get('user_name', '')
        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.tier = int(self.event.get('tier', 1000))
        self.is_gift = True if self.event.get('is_gift', False) else False

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A SubscribeEvent was received: {self}')
        if not self.is_gift:
            message = f'Thank you so much for subscribing {self.user_name}!'

        else:
            message = f'{self.user_name} was just gifted a subscription!'

        await bot.send_message(message)

        # Update the stream stats table.
        last_row = dict(await bot.db.get_last_row('stream_stats'))
        await bot.db.update(
            'stream_stats',
            {'subscribers': last_row['subscribers'] + 1},
            {'id': last_row['id']},
        )

        await bot.loyalty_manager.add_loyalty_points_for_event(
            self.user_name, 'subscribe'
        )


class SubscriptionGiftEvent(EventSubEvent):
    """Subscription gift event."""

    def __init__(self) -> None:
        """Init."""
        super(SubscriptionGiftEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.user_id = int(self.event.get('user_id', 0))
        self.user_login = self.event.get('user_login', '')
        self.user_name = self.event.get('user_name', '')
        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.total = int(self.event.get('total', 0))
        self.tier = int(self.event.get('tier', 1000))
        self.cumulative_total = self.event.get('cumulative_total', 0)
        self.is_anonymous = (
            True if self.event.get('is_anonymous', False) else False
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A SubscriptionGiftEvent was received: {self}')
        user_name = (
            'An anonymous user' if self.is_anonymous else self.user_name
        )
        await bot.send_message(
            f'{user_name} has generously gifted a subscription!'
        )


class SubscriptionMessageEvent(EventSubEvent):
    """Subscription message event."""

    def __init__(self) -> None:
        """Init."""
        super(SubscriptionMessageEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.user_id = int(self.event.get('user_id', 0))
        self.user_login = self.event.get('user_login', '')
        self.user_name = self.event.get('user_name', '')
        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.tier = int(self.event.get('tier', 1000))
        self.message = self.event.get('message', {}).get('text', '')
        self.cumulative_months = int(self.event.get('cumulative_months', 0))
        self.streak_months = self.event.get('streak_months', 0)
        self.duration_months = int(self.event.get('duration_months', 0))

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A SubscriptionMessageEvent was received: {self}')

        is_resub = 're-' if self.cumulative_months > 1 else ''

        if self.message:
            user_message = ' and said: "' + self.message + '".'
        else:
            user_message = ''

        await bot.send_message(
            f'{self.user_name} just {is_resub}subscribed for '
            f'x{self.cumulative_months}{user_message}. Thank you!'
        )

        # Update the stream stats table.
        last_row = dict(await bot.db.get_last_row('stream_stats'))
        await bot.db.update(
            'stream_stats',
            {'subscribers': last_row['subscribers'] + 1},
            {'id': last_row['id']},
        )

        await bot.loyalty_manager.add_loyalty_points_for_event(
            self.user_name, 'subscribe'
        )


class CheerEvent(EventSubEvent):
    """Cheer event."""

    def __init__(self) -> None:
        """Init."""
        super(CheerEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.is_anonymous = (
            True if self.event.get('is_anonymous', False) else False
        )
        self.user_id = int(self.event.get('user_id', 0))
        self.user_login = self.event.get('user_login', '')
        self.user_name = self.event.get('user_name', '')
        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.message = self.event.get('message', '')
        self.bits = int(self.event.get('bits', 0))

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A CheerEvent was received: {self}')
        user_name = (
            'An anonymous user' if self.is_anonymous else self.user_name
        )

        if self.message:
            user_message = ' and said: "' + self.message + '".'
        else:
            user_message = ''

        await bot.send_message(
            f'{user_name} just generously cheered {self.bits} bits'
            f'{user_message}. You are awesome!'
        )

        # Update the stream stats table.
        last_row = dict(await bot.db.get_last_row('stream_stats'))
        await bot.db.update(
            'stream_stats',
            {'bits': last_row['bits'] + self.bits},
            {'id': last_row['id']},
        )

        await bot.loyalty_manager.add_loyalty_points_for_event(
            self.user_name, 'cheer'
        )


class RaidEvent(EventSubEvent):
    """Raid event."""

    def __init__(self) -> None:
        """Init."""
        super(RaidEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.from_broadcaster_user_id = int(
            self.event.get('from_broadcaster_user_id', 0)
        )
        self.from_broadcaster_user_login = self.event.get(
            'from_broadcaster_user_login', ''
        )
        self.from_broadcaster_user_name = self.event.get(
            'from_broadcaster_user_name', ''
        )
        self.to_broadcaster_user_id = int(
            self.event.get('to_broadcaster_user_id', 0)
        )
        self.to_broadcaster_user_login = self.event.get(
            'to_broadcaster_user_login', ''
        )
        self.to_broadcaster_user_name = self.event.get(
            'to_broadcaster_user_name', ''
        )

        self.viewers = int(self.event.get('viewers', 0))

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A RaidEvent was received: {self}')
        await bot.send_message(
            f'{self.from_broadcaster_user_name} just raided! '
            'Thank you, and welcome raiders!'
        )

        # Call the shoutout plugin automatically.
        user = await api.get_user_data(bot.auth, bot.owner)
        await bot.dispatch_command(
            event=self,
            user=user,
            command='so',
            command_args=[self.from_broadcaster_user_name],
        )

        # Update the stream stats table.
        last_row = dict(await bot.db.get_last_row('stream_stats'))
        await bot.db.update(
            'stream_stats',
            {'raids': last_row['raids'] + 1},
            {'id': last_row['id']},
        )


class RewardRedemptionEvent(EventSubEvent):
    """Reward redemption event."""

    def __init__(self) -> None:
        """Init."""
        super(RewardRedemptionEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.user_id = int(self.event.get('user_id', 0))
        self.user_login = self.event.get('user_login', '')
        self.user_name = self.event.get('user_name', '')
        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.id = self.event.get('id', '0')
        self.status = self.event.get('status', 'unfulfilled')
        self.reward = self.event.get('reward', {})
        self.reward_id = self.reward.get('id', 0)
        self.reward_title = self.reward.get('title', '')
        self.reward_cost = int(self.reward.get('cost', 0))
        self.reward_prompt = self.reward.get('prompt', '')
        self.redeemed_at = datetime.now()

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A RewardRedemptionEvent was received: {self}')
        # Update the stream stats table.
        last_row = dict(await bot.db.get_last_row('stream_stats'))
        await bot.db.update(
            'stream_stats',
            {'rewards': last_row['rewards'] + 1},
            {'id': last_row['id']},
        )

        parts = self.reward_title.split(' ')
        command = parts[0].lower()
        command_args = []

        # Some arguments might be included in the reward name.
        if len(parts) > 1:
            command_args.extend(parts[1:])

        # Rewards can offer a prompt to the user, so if a reply exists,
        # add it to the arguments.
        if self.reward_prompt:
            command_args.append(self.reward_prompt)

        # If a plugin is associated with the reward, run it.
        redemption_plugins = bot.plugins.get('redemption', {})
        if command in redemption_plugins:
            plugin = redemption_plugins[command]
            user = {'name': self.user_name, 'id': self.user_id}

            LOG.debug(f'Running {plugin} for {self.reward_title} redemption')
            await bot._run_plugin(plugin, self, user, command, command_args)


class RewardRedemptionUpdateEvent(EventSubEvent):
    """Reward redemption update event."""

    def __init__(self) -> None:
        """Init."""
        super(RewardRedemptionUpdateEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.user_id = int(self.event.get('user_id', 0))
        self.user_login = self.event.get('user_login', '')
        self.user_name = self.event.get('user_name', '')
        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.id = self.event.get('id', '0')
        self.status = self.event.get('status', 'fulfilled')
        self.reward = self.event.get('reward', {})
        self.reward_id = self.reward.get('id', 0)
        self.reward_title = self.reward.get('title', '')
        self.reward_cost = int(self.reward.get('cost', 0))
        self.reward_prompt = self.reward.get('prompt', '')
        self.redeemed_at = await utils.parse_datetime(
            self.event.get('redeemed_at', '')
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A RewardRedemptionUpdateEvent was received: {self}')


class GoalProgressEvent(EventSubEvent):
    """Goal progress event."""

    def __init__(self) -> None:
        """Init."""
        super(GoalProgressEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.id = self.event.get('id', '0')
        self.description = self.event.get('description', '')
        self.current_amount = int(self.event.get('current_amount', 0))
        self.target_amount = int(self.event.get('target_amount', 0))
        self.started_at = await utils.parse_datetime(
            self.event.get('started_at', '')
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A GoalProgressEvent was received: {self}.')


class GoalEndEvent(EventSubEvent):
    """Goal end event."""

    def __init__(self) -> None:
        """Init."""
        super(GoalEndEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.id = self.event.get('id', '0')
        self.description = self.event.get('description', '')
        self.is_achieved = self.event.get('is_achieved', False)
        self.current_amount = int(self.event.get('current_amount', 0))
        self.target_amount = int(self.event.get('target_amount', 0))
        self.started_at = await utils.parse_datetime(
            self.event.get('started_at', '')
        )
        self.ended_at = await utils.parse_datetime(
            self.event.get('ended_at', '')
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A GoalEndEvent was received: {self}.')


class HypeTrainBeginEvent(EventSubEvent):
    """Hype train begin event."""

    def __init__(self) -> None:
        """Init."""
        super(HypeTrainBeginEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.id = self.event.get('id', '0')
        self.total = int(self.event.get('total', 0))
        self.progress = int(self.event.get('progress', 0))
        self.goal = int(self.event.get('goal', 0))
        self.top_contributions = self.event.get('top_contributions', [])
        self.last_contribution = self.event.get('last_contribution', {})
        self.started_at = await utils.parse_datetime(
            self.event.get('started_at', '')
        )
        self.expires_at = await utils.parse_datetime(
            self.event.get('expires_at', '')
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A HypeTrainBeginEvent was received: {self}')


class HypeTrainProgressEvent(EventSubEvent):
    """Hype train progress event."""

    def __init__(self) -> None:
        """Init."""
        super(HypeTrainProgressEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.id = self.event.get('id', '0')
        self.level = int(self.event.get('level', 0))
        self.total = int(self.event.get('total', 0))
        self.progress = int(self.event.get('progress', 0))
        self.goal = int(self.event.get('goal', 0))
        self.top_contributions = self.event.get('top_contributions', [])
        self.last_contribution = self.event.get('last_contribution', {})
        self.started_at = await utils.parse_datetime(
            self.event.get('started_at', '')
        )
        self.expires_at = await utils.parse_datetime(
            self.event.get('expires_at', '')
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A HypeTrainProgressEvent was received: {self}')


class HypeTrainEndEvent(EventSubEvent):
    """Hype train end event."""

    def __init__(self) -> None:
        """Init."""
        super(HypeTrainEndEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.id = self.event.get('id', '0')
        self.level = int(self.event.get('level', 0))
        self.total = int(self.event.get('total', 0))
        self.top_contributions = self.event.get('top_contributions', [])
        self.started_at = await utils.parse_datetime(
            self.event.get('started_at', '')
        )
        self.expires_at = await utils.parse_datetime(
            self.event.get('expires_at', '')
        )
        self.cooldown_ends_at = await utils.parse_datetime(
            self.event.get('cooldown_ends_at', '')
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A HypeTrainEndEvent was received: {self}.')


class StreamOnlineEvent(EventSubEvent):
    """Stream online event."""

    def __init__(self) -> None:
        """Init."""
        super(StreamOnlineEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        self.id = self.event.get('id', '0')
        self.type = self.event.get('type', 'live')
        self.started_at = await utils.parse_datetime(
            self.event.get('started_at', '')
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A StreamOnlineEvent was received: {self}.')

        # Long running streams will result in this event getting sent every
        # ~5 hours, so ignore it if the bot is already running.
        if bot.running:
            LOG.debug('Bot is already running.')
            return

        bot.running = True

        # Get stream info.
        channel_data = await api.get_channel_data(bot.auth, bot.owner)

        # Send a message to Discord that the stream is online.
        await discord_sender.send_online_announcement(channel_data)

        # Create a new stats entry.
        await bot.db.insert(
            'stream_stats',
            {'stream_end': datetime.now(), 'stream_start': datetime.now()},
        )

        # Connect OBS if it is not already connected.
        await bot.obs.obs_connection.connect()


class StreamOfflineEvent(EventSubEvent):
    """Stream offline event."""

    def __init__(self) -> None:
        """Init."""
        super(StreamOfflineEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Event data.

        Returns:
            self (object): self
        """
        self.data = data
        self.event = data.get('event', {})

        self.broadcaster_user_id = int(
            self.event.get('broadcaster_user_id', 0)
        )
        self.broadcaster_user_login = self.event.get(
            'broadcaster_user_login', ''
        )
        self.broadcaster_user_name = self.event.get(
            'broadcaster_user_name', ''
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A StreamOfflineEvent was received: {self}.')
        self.bot = bot

        # Disconnect OBS
        await self.bot.obs.obs_connection.disconnect()

        # Update the stream stats database.
        chatters_cache = await CACHE.get('chatters')
        last_row = dict(await self.bot.db.get_last_row('stream_stats'))
        await self.bot.db.update(
            'stream_stats',
            {
                'chatters': len(chatters_cache.data),
                'stream_end': str(datetime.now()),
            },
            {'id': last_row['id']},
        )

        await self.part_all_users()
        await self.graph_stats()

        # Clear the user cache.
        user_cache = await CACHE.get('users')
        user_cache.data = []

        # Clear the chatters cache.
        chatters_cache.data = []

        bot.running = False

        LOG.info('Stream Offline Event completed.')

    async def part_all_users(self) -> None:
        """Run the user part code for all users in chat."""
        # Access cache of users in chat.
        users = await CACHE.get('users')

        for user in users.data:
            # Skip the owner and bot
            if user in [self.bot.owner, self.bot.username]:
                continue

            # Since we are using the existing part event, we create a dummy
            # IRC message with the user in it since only the username matters
            # here.
            data = (
                f':{user}!{user}@{user}.tmi.twitch.tv '
                'PRIVMSG #descvert :dummy message'
            )
            part_event = await PartEvent().init(data)
            await part_event.run(self.bot)

    async def graph_stats(self) -> None:
        """Graph the stream stats."""
        # Call the graph_stats plugin automatically.
        user_data = await api.get_user_data(self.bot.auth, self.bot.owner)
        user = {'name': user_data['display_name'], 'id': user_data['id']}
        await self.bot._run_plugin(
            plugin=self.bot.plugins['command']['graph_stats'],
            event=self,
            user=user,
            command='graph_stats',
            command_args=[],
        )
