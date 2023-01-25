#!/usr/bin/env python

"""Test of the Tortoise ORM Models."""

from tortoise import fields
from tortoise.models import Model


class Users(Model):
    """Users table model."""

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    user_id = fields.IntField(unique=True)
    is_mod = fields.BooleanField(default=False)
    is_regular = fields.BooleanField(default=False)
    is_banned = fields.BooleanField(default=False)
    ban_until = fields.CharField(max_length=255, default='1970-01-01 00:00:00')
    time_watched = fields.IntField(default=0)
    messages_sent_session = fields.IntField(default=0)
    messages_sent_total = fields.IntField(default=0)
    first_join_time = fields.CharField(
        max_length=255, default='1970-01-01 00:00:00'
    )
    last_join_time = fields.CharField(
        max_length=255, default='1970-01-01 00:00:00'
    )
    last_leave_time = fields.CharField(
        max_length=255, default='1970-01-01 00:00:00'
    )
    announce = fields.BooleanField(default=False)
    points = fields.IntField(default=0)
    loyalty_points = fields.IntField(default=0)

    class Meta:
        table = 'users'
        indexes = ('username', 'user_id')

    def as_dict(self) -> dict:
        data_dict = {
            'id': self.id,
            'username': self.username,
            'user_id': self.user_id,
            'is_mod': self.is_mod,
            'is_regular': self.is_regular,
            'is_banned': self.is_banned,
            'ban_until': self.ban_until,
            'time_watched': self.time_watched,
            'messages_sent_session': self.messages_sent_session,
            'messages_sent_total': self.messages_sent_total,
            'first_join_time': self.first_join_time,
            'last_join_time': self.last_join_time,
            'last_leave_time': self.last_leave_time,
            'announce': self.announce,
            'points': self.points,
            'loyalty_points': self.loyalty_points,
        }
        return data_dict

    def __str__(self) -> str:
        data_dict = self.as_dict()
        return ', '.join([f'{k}: {data_dict[k]}' for k in data_dict])


class ViewerStats(Model):
    """Viewer stats table model."""

    id = fields.IntField(pk=True)
    date = fields.CharField(max_length=255, default='1970-01-01')
    time = fields.CharField(max_length=255, default='00:00:00')
    viewer_count = fields.IntField(default=0)

    class Meta:
        table = 'viewer_stats'

    def as_dict(self) -> dict:
        data_dict = {
            'id': self.id,
            'date': self.date,
            'time': self.time,
            'viewer_count': self.viewer_count,
        }
        return data_dict

    def __str__(self) -> str:
        data_dict = self.as_dict()
        return ', '.join([f'{k}: {data_dict[k]}' for k in data_dict])


class StreamStats(Model):
    """Stream stats table model."""

    id = fields.IntField(pk=True)
    bits = fields.IntField(default=0)
    chatters = fields.IntField(default=0)
    followers = fields.IntField(default=0)
    messages = fields.IntField(default=0)
    raids = fields.IntField(default=0)
    rewards = fields.IntField(default=0)
    stream_end = fields.CharField(
        max_length=255, default='1970-01-01 00:00:00'
    )
    stream_start = fields.CharField(
        max_length=255, default='1970-01-01 00:00:00'
    )
    subscribers = fields.IntField(default=0)

    class Meta:
        table = 'stream_stats'

    def as_dict(self) -> dict:
        data_dict = {
            'id': self.id,
            'bits': self.bits,
            'chatters': self.chatters,
            'followers': self.followers,
            'messages': self.messages,
            'raids': self.raids,
            'rewards': self.rewards,
            'stream_end': self.stream_end,
            'stream_start': self.stream_start,
            'subscribers': self.subscribers,
        }
        return data_dict

    def __str__(self) -> str:
        data_dict = self.as_dict()
        return ', '.join([f'{k}: {data_dict[k]}' for k in data_dict])


class StreamEvents(Model):
    """Stream events table model."""

    id = fields.IntField(pk=True)
    stream_end = fields.CharField(
        max_length=255, default='1970-01-01 00:00:00'
    )
    stream_start = fields.CharField(
        max_length=255, default='1970-01-01 00:00:00'
    )
    usernames = fields.CharField(max_length=255)

    class Meta:
        table = 'stream_events'

    def as_dict(self) -> dict:
        data_dict = {
            'id': self.id,
            'stream_end': self.stream_end,
            'stream_start': self.stream_start,
            'usernames': self.usernames,
        }
        return data_dict

    def __str__(self) -> str:
        data_dict = self.as_dict()
        return ', '.join([f'{k}: {data_dict[k]}' for k in data_dict])
