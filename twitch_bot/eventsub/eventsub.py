"""EventSub."""

import json
import traceback

from typing import Optional

import api
import auth
import server_utils

import ngrok

from configs import config_utils
from exceptions import exceptions
from log import LOG


class EventSub(object):
    """EventSub."""

    def __init__(self):
        """Init."""
        super(EventSub, self).__init__()

    async def init(self, authorization: Optional[auth.Auth] = None) -> object:
        """Async init.

        Args:
            authorization (Auth, optional): Auth object.

        ReturnsL
            (EventSub): This class instance.
        """
        self.config = await config_utils.load_config_file('bot_config')
        self.auth = authorization or await auth.Auth().init(self.config)
        self.owner = self.config.get('owner')
        self.username = self.config.get('username')
        self.channel = f'#{self.owner}'

        # Get the owner's channel data.
        self.channel_data = await api.get_channel_data(
            self.auth, self.config.get('owner')
        )
        self.channel_id = self.channel_data.get('id')

        self.subscriptions = self.config.get('eventsub_subscriptions', [])

        # Get the public ngrok url
        self.ngrok_url = await ngrok.get_url()
        if not self.ngrok_url:
            raise exceptions.NgrokError(
                'ngrok is not running. A public URL is needed to run this bot.'
            )

        # If the ngrok tunnel is dynamic,
        # delete and recreate the subscriptions.
        if not await ngrok.is_static():
            await self.delete_subscriptions()
            await self.create_subscriptions()

        # Otherwise just fill in any missing sibscriptions.
        else:
            await self.fill_missing_subscriptions()

        return self

    async def create_subscriptions(self) -> None:
        """Create subscriptions to EventSub."""
        for sub in self.subscriptions:
            await self.create_subscription(sub)

    async def create_subscription(self, subscription: str) -> None:
        """Create a subscription.

        Args:
            subscription (str): Subscription name.
        """
        LOG.debug(f'Subscribing to {subscription}')
        url = self.config.get('eventsub_url')

        headers = {
            'Client-ID': self.auth.client_id,
            'Authorization': f'Bearer {self.auth.bearer}',
            'Content-Type': 'application/json',
        }

        data = {
            'type': subscription,
            'version': '1',
            'transport': {
                'method': 'webhook',
                'callback': f'{self.ngrok_url}/events',
                'secret': self.auth.eventsub_secret,
            },
        }

        # channel.raid uses a different condition
        if subscription == 'channel.raid':
            data['condition'] = {'to_broadcaster_user_id': self.channel_id}
        else:
            data['condition'] = {'broadcaster_user_id': self.channel_id}

        LOG.debug(data)
        json_data = json.dumps(data)

        response = await server_utils.post_request(url, json_data, headers)
        LOG.debug(response)

    async def list_subscriptions(self, status: Optional[str] = None) -> dict:
        """List all active subscriptions.

        Args:
            status (str, optional): Status filter.
                Possible status values:
                    enabled,
                    webhook_callback_verification_pending,
                    webhook_callback_verification_failed,
                    notification_failures_exceeded,
                    authorization_revoked,
                    user_removed

        Returns:
            (dict): Subscription data from Twitch.
        """
        LOG.debug('Getting subscriptions')
        url = self.config.get('eventsub_url')

        headers = {
            'Client-ID': self.auth.client_id,
            'Authorization': f'Bearer {self.auth.bearer}',
        }

        params = {'status': status} if status else {}

        response, data = await server_utils.get_request(url, headers, params)
        LOG.debug(data)
        return data

    async def fill_missing_subscriptions(self) -> None:
        """Add any subscriptions that are missing.

        These are subscriptions that are in the config, but not in the list of
        subscriptions from Twitch.
        """
        message = await self.list_subscriptions()
        data = message.get('data', [])
        active_subscriptions = [s['type'] for s in data]
        for subscription in self.subscriptions:
            if subscription in active_subscriptions:
                continue

            await self.create_subscription(subscription)

    async def delete_subscriptions(self) -> None:
        """Delete EventSub subscriptions."""
        message = await self.list_subscriptions()
        subscriptions = message.get('data', [])
        for subscription in subscriptions:
            subscription_id = subscription['id']
            try:
                await self.delete_subscription(subscription_id)
            except Exception:
                LOG.error(
                    f'Unable to delete subscription with id: {subscription_id}'
                )
                traceback.print_exc()

    async def delete_subscription(self, subscription_id: str) -> None:
        """Delete a subscription.

        Args:
            subscription_id (str): Subscription id.
        """
        LOG.debug(f'Deleting {subscription_id}')
        url = self.config.get('eventsub_url')

        headers = {
            'Client-ID': self.auth.client_id,
            'Authorization': f'Bearer {self.auth.bearer}',
        }

        params = {'id': subscription_id}

        response = await server_utils.delete_request(url, headers, params)
        LOG.debug(response)
