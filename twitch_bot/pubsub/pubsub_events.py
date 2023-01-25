"""PubSub Events."""

from datetime import datetime

from events import Event
from log import LOG


class PubSubEvent(Event):
    """PubSub event."""

    def __init__(self) -> None:
        """Init."""
        super(PubSubEvent, self).__init__()


class AutoModQueueEvent(PubSubEvent):
    """AutoMod Queue event."""

    def __init__(self) -> None:
        """Init."""
        super(AutoModQueueEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Pubsub message.

        Returns:
            self (object): self.
        """
        message = data.get('message', {}).get('data', {}).get('message', {})

        self.id = message.get('id', '')
        self.content = message.get('content', {})
        self.content_text = self.content.get('text', '')
        self.content_fragments = self.content.get('fragments', [])

        self.sender = message.get('sender', {})
        self.sender_user_id = int(self.sender.get('user_id', 0))
        self.sender_login = self.sender.get('login', '')
        self.sender_display_name = self.sender.get('display_name', '')
        self.sender_chat_color = self.sender.get('chat_color', '')
        self.sent_at = message.get('sent_at', datetime.now())

        self.content_classification = (
            data.get('message', {})
            .get('data', {})
            .get('content_classification', {})
        )
        self.content_classification_category = self.content_classification.get(
            'category', ''
        )
        self.content_classification_level = self.content_classification.get(
            'level', 0
        )

        self.status = data.get('message', {}).get('data', {}).get('status', '')
        self.reason_code = (
            data.get('message', {}).get('data', {}).get('reason_code', '')
        )
        self.resolver_id = (
            data.get('message', {}).get('data', {}).get('resolver_id', '')
        )
        self.resolver_login = (
            data.get('message', {}).get('data', {}).get('resolver_login', '')
        )

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A AutoModQueueEvent was received: {self}.')


class BitsEvent(PubSubEvent):
    """Bits event."""

    def __init__(self) -> None:
        """Init."""
        super(BitsEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Pubsub message.

        Returns:
            self (object): self.
        """
        message = data.get('message', {})

        self.user_name = message.get('user_name', '')
        self.channel_name = message.get('channel_name', '')
        self.user_id = int(message.get('user_id', 0))
        self.channel_id = int(message.get('channel_id', 0))
        self.time = message.get('time', datetime.now())
        self.chat_message = message.get('chat_message', '')
        self.bits_used = int(message.get('bits_used', 0))
        self.total_bits_used = int(message.get('total_bits_used', 0))
        self.context = message.get('context', '')

        badge_entitlement = message.get('badge_entitlement', {})
        self.new_version = int(badge_entitlement.get('new_version', 0))
        self.previous_version = int(
            badge_entitlement.get('previous_version', 0)
        )

        self.is_anonymous = data.get('is_anonymous', False)

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A BitsEvent was received: {self}.')


class BitsBadgeEvent(PubSubEvent):
    """Bits badge event."""

    def __init__(self) -> None:
        """Init."""
        super(BitsBadgeEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Pubsub message.

        Returns:
            self (object): self.
        """
        message = data.get('message', {})

        self.user_id = int(message.get('user_id', 0))
        self.user_name = message.get('user_name', '')
        self.channel_id = int(message.get('channel_id', 0))
        self.channel_name = message.get('channel_name', '')
        self.badge_tier = int(message.get('badge_tier', 0))
        self.chat_message = message.get('chat_message', '')
        self.time = message.get('time', datetime.now())

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A BitsBadgeEvent was received: {self}.')


class ChatModeratorActionsEvent(PubSubEvent):
    """Chat moderator actions event.

    Although listed in the possible topics, this event has no documentation
    and no way to trigger it as a test. This will act as a placeholder until
    the data received from this event can be confirmed.
    """

    def __init__(self) -> None:
        """Init."""
        super(ChatModeratorActionsEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Pubsub message.

        Returns:
            self (object): self.
        """
        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A ChatModeratorActionsEvent was received: {self}.')


class ChannelPointsEvent(PubSubEvent):
    """Channel points event."""

    def __init__(self) -> None:
        """Init."""
        super(ChannelPointsEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Pubsub message.

        Returns:
            self (object): self.
        """
        self.id = data.get('id', '')

        self.user = data.get('user', {})
        self.user_id = int(self.user.get('id', 0))
        self.login = self.user.get('login', '')
        self.display_name = self.user.get('display_name', '')

        self.channel_id = int(data.get('channel_id', 0))
        self.redeemed_at = data.get('redeemed_at', datetime.now())

        self.reward = data.get('reward', {})
        self.reward_id = int(self.reward.get('id', 0))
        self.channel_id = self.reward.get('channel_id', '')
        self.title = self.reward.get('title', '')
        self.prompt = self.reward.get('prompt', '')
        self.cost = int(self.reward.get('cost', 0))
        self.is_user_input_required = self.reward.get(
            'is_user_input_required', False
        )
        self.is_sub_only = self.reward.get('is_sub_only', False)

        self.image = self.reward.get('image', {})
        self.image_url_1x = self.image.get('url_1x', '')
        self.image_url_2x = self.image.get('url_2x', '')
        self.image_url_4x = self.image.get('url_4x', '')

        self.default_image = self.reward.get('default_image', {})
        self.default_image_url_1x = self.image.get('url_1x', '')
        self.default_image_url_2x = self.image.get('url_2x', '')
        self.default_image_url_4x = self.image.get('url_4x', '')

        self.background_color = self.reward.get('background_color', '#000000')
        self.is_enabled = self.reward.get('is_enabled', True)
        self.is_paused = self.reward.get('is_paused', False)
        self.is_in_stock = self.reward.get('is_in_stock', True)

        self.max_per_stream = self.reward.get('max_per_stream', {})
        self.max_is_enabled = self.max_per_stream.get('is_enabled', False)
        self.max_max_per_stream = int(
            self.max_per_stream.get('max_per_stream', 0)
        )

        self.should_redemptions_skip_request_queue = self.reward.get(
            'should_redemptions_skip_request_queue', False
        )

        self.user_input = data.get('user_input', '')
        self.status = data.get('status', '')

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A ChannelPointsEvent was received: {self}.')


class SubscribeEvent(PubSubEvent):
    """Subscribe event."""

    def __init__(self) -> None:
        """Init."""
        super(SubscribeEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Pubsub message.

        Returns:
            self (object): self.
        """
        message = data.get('message', {})

        self.user_name = message.get("user_name", '')
        self.display_name = message.get("display_name", '')
        self.channel_name = message.get("channel_name", '')
        self.user_id = int(message.get("user_id", 0))
        self.channel_id = int(message.get("channel_id", 0))
        self.time = message.get("time", datetime.now())
        self.sub_plan = int(message.get("sub_plan", 0))
        self.sub_plan_name = message.get("sub_plan_name", '')
        self.months = int(message.get("months", 0))
        self.context = message.get("context", '')
        self.is_gift = message.get("is_gift", False)

        self.sub_message = message.get("sub_message", {})
        self.message = self.sub_message.get("message", "")
        self.emotes = self.sub_message.get("emotes", [])

        self.recipient_id = int(message.get("recipient_id", 0))
        self.recipient_user_name = message.get("recipient_user_name", '')
        self.recipient_display_name = message.get("recipient_display_name", '')

        self.multi_month_duration = int(message.get("multi_month_duration", 0))

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A SubscribeEvent was received: {self}.')


class UserModerationEvent(PubSubEvent):
    """User moderation event."""

    def __init__(self) -> None:
        """Init."""
        super(UserModerationEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Pubsub message.

        Returns:
            self (object): self.
        """
        message = data.get('message', {})

        self.message_type = message.get('type', '')
        self.data = message.get('data', {})
        self.data_message_id = self.data.get('message_id', '')
        self.data_status = self.data.get('status', '')

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A UserModerationEvent was received: {self}.')


class WhisperEvent(PubSubEvent):
    """Whisper event."""

    def __init__(self) -> None:
        """Init."""
        super(WhisperEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Pubsub message.

        Returns:
            self (object): self.
        """
        message = data.get('message', {})

        self.message_type = message.get('type', '')
        self.data = message.get('data', {})
        self.message_data_id = int(self.data.get('id', 0))

        self.message_thread_id = message.get('thread_id', '')
        self.message_body = message.get('body', '')
        self.message_sent_ts = message.get(
            'sent_ts', int(datetime.now().timestamp())
        )
        self.message_from_id = int(message.get('from_id', 0))

        self.message_tags = message.get('tags', {})
        self.message_tags_login = self.message_tags.get('login', '')
        self.message_tags_display_name = self.message_tags.get(
            'display_name', ''
        )
        self.message_tags_color = self.message_tags.get('color', '')
        self.message_tags_emotes = self.message_tags.get('emotes', [])
        self.message_tags_badges = self.message_tags.get('badges', [])

        self.message_recipient = message.get('recipient', {})
        self.message_recipient_id = int(self.message_recipient.get('id', 0))
        self.message_recipient_username = self.message_recipient.get(
            'username', ''
        )
        self.message_recipient_display_name = self.message_recipient.get(
            'display_name', ''
        )
        self.message_recipient_color = self.recipient.get('color', '')
        self.message_recipient_badges = self.recipient.get('badges', [])

        data_object = data.get('data_object', {})

        self.data_object_id = int(self.data.get('id', 0))
        self.data_object_thread_id = data_object.get('thread_id', '')
        self.data_object_body = data_object.get('body', '')
        self.data_object_sent_ts = data_object.get(
            'sent_ts', int(datetime.now().timestamp())
        )
        self.data_object_from_id = int(data_object.get('from_id', 0))

        self.data_object_tags = data_object.get('tags', {})
        self.data_object_tags_login = self.tags.get('login', '')
        self.data_object_tags_display_name = self.tags.get('display_name', '')
        self.data_object_tags_color = self.tags.get('color', '')
        self.data_object_tags_emotes = self.tags.get('emotes', [])
        self.data_object_tags_badges = self.tags.get('badges', [])

        self.data_object_recipient = data_object.get('recipient', {})
        self.data_object_recipient_id = int(self.recipient.get('id', 0))
        self.data_object_recipient_username = self.recipient.get(
            'username', ''
        )
        self.data_object_recipient_display_name = self.recipient.get(
            'display_name', ''
        )
        self.data_object_recipient_color = self.recipient.get('color', '')
        self.data_object_recipient_badges = self.recipient.get('badges', [])

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A WhisperEvent was received: {self}.')


class PongEvent(PubSubEvent):
    """Pong event."""

    def __init__(self) -> None:
        """Init."""
        super(PongEvent, self).__init__()

    async def init(self, data: dict) -> object:
        """Async init.

        Args:
            data (dict): Pubsub message.

        Returns:
            self (object): self.
        """
        self.data = data

        return self

    async def run(self, bot: object) -> None:
        """Run the code triggered by the event.

        Args:
            bot (Bot): Bot instance.
        """
        LOG.debug(f'A PongEvent was received: {self}.')
