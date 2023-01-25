"""Authentication Class."""

import uuid

from configs import config_utils
from exceptions import exceptions
from log import LOG
from server_utils import get_request, post_request


class Auth(object):
    """Authentication Object.

    This is used to automatically handle the authorization of the bot to
    Twitch and any calls made to it.
    """

    def __init__(self) -> None:
        """Init."""
        super(Auth, self).__init__()

    async def init(self, twitch_config: dict = None) -> object:
        """Async init.

        Args:
            twitch_config (dict): Twitch config file name.
                If not given, the default twitch_config is used.
        """
        # Load the config.
        self.twitch_config = (
            twitch_config
            if twitch_config
            else await config_utils.load_config_file('bot_config')
        )

        # Load the secrets.
        await self.load_secrets()

        # Generate a state value.
        # This is used to authenticate messages to ensure they came back
        # from the result of your message to Twitch.
        self.state = uuid.uuid1().hex

        # Generate a bearer token.
        self.bearer = await self._get_bearer_token()

        # Validate the tokens and renew them if needed.
        await self._validate_bearer()
        try:
            await self._validate_access_token()
        except Exception:
            LOG.error('Unable to validate access token.')

        return self

    async def load_secrets(self) -> None:
        """Load the secrets from the config file."""
        # Load Twitch secrets.
        self.twitch_secrets = await config_utils.load_config_file(
            'secrets', refresh=True
        )

        self.client_id = self.twitch_secrets.get('client_id')
        self.irc_oauth = self.twitch_secrets.get('irc_oauth')
        self.secret = self.twitch_secrets.get('secret')
        self.oauth = self.twitch_secrets.get('oauth_token')
        self.access_token = self.twitch_secrets.get('access_token')
        self.refresh = self.twitch_secrets.get('refresh')
        self.eventsub_secret = self.twitch_secrets.get('eventsub_secret')
        self.discord_token = self.twitch_secrets.get('discord_token')
        self.obs_password = self.twitch_secrets.get('obs_websockets_pass')

    async def _get_bearer_token(self) -> str:
        """Get a bearer (application) token.

        Returns:
            (str): App access token.
        """
        LOG.debug('Getting bearer token.')
        url = 'https://id.twitch.tv/oauth2/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.secret,
            'grant_type': 'client_credentials',
        }

        if self.twitch_config.get('scopes', None):
            data['scope'] = ' '.join(self.twitch_config.get('chat_scopes'))

        response_code, new_data = await post_request(url, data)
        if response_code != 200:
            raise exceptions.AuthError('Unable to validate bearer_token.')

        return new_data.get('access_token')

    async def _validate_bearer(self) -> dict:
        """Validate the bearer token via OAuth.

        Returns:
            (dict): Response from validation.
        """
        LOG.debug('Validating bearer token.')
        url = 'https://id.twitch.tv/oauth2/validate'
        headers = {
            'client-id': self.client_id,
            'Authorization': 'OAuth {}'.format(self.bearer),
        }

        response_code, data = await get_request(url, headers)
        if response_code != 200:
            await self._get_bearer_token()
            LOG.debug('Bearer token validated.')

        return data

    async def _validate_access_token(self) -> dict:
        """Validate the access token via OAuth.

        Returns:
            (dict): Response from validation.
        """
        LOG.debug('Validating access token.')
        url = 'https://id.twitch.tv/oauth2/validate'
        headers = {'Authorization': 'OAuth {}'.format(self.access_token)}

        response_code, data = await get_request(url, headers)
        if response_code != 200:
            await self._refresh_token()

            # Reload the secrets after refreshing the tokens.
            await self.load_secrets()

        return data

    async def validate_tokens(self) -> None:
        """Validae all tokens."""
        await self._validate_bearer()
        await self._validate_access_token()

    async def _refresh_token(self):
        """Refresh the OAuth token."""
        LOG.info('Refreshing access token...')
        url = 'https://id.twitch.tv/oauth2/token'
        data = {
            'access_token': self.access_token,
            'client_id': self.client_id,
            'client_secret': self.secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh,
        }

        response_code, new_data = await post_request(url, data)
        if response_code != 200:
            raise exceptions.AuthError('Unable to refresh access_token.')

        await config_utils.write_config_values(
            'secrets', {'access_token': new_data['access_token']}
        )

        LOG.info('Access token successfully refreshed.')

        return data

    async def generate_permissions_url(self) -> str:
        """Generate the URL that will be sent to the user.

        This URL will prompt the user to authorize the bot to see private
        channel data. The users response to the prompt is sent to the
        redirect_uri. The response can be validated using the state key.

        Returns:
            url (str): The URL for authorizing the bot.
        """
        url = (
            'https://id.twitch.tv/oauth2/authorize'
            '?client_id={client_id}'
            '&redirect_uri=http://localhost/auth'
            '&response_type=code'
            '&scope={scope}'
            '&state={state}'.format(
                client_id=self.client_id,
                scope=' '.join(self.twitch_config.get('oauth_scopes')),
                state=self.state,
            )
        )

        return url

    async def get_access_token(self, code: str) -> dict:
        """Authorize the oauth token and get the token data.

        Args:
            code (str): Token generated by the user confirming access to the
                bot.

        Returns:
            (dict): Response from Twitch with the access token, refresh token,
                and scope information.
        """
        url = 'https://id.twitch.tv/oauth2/token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost/auth',
        }

        response_code, new_data = await post_request(url, data)
        if response_code != 200:
            raise exceptions.AuthError('Unable to get access_token.')

        await config_utils.write_config_values(
            'secrets',
            {
                'access_token': new_data['access_token'],
                'refresh': new_data['refresh_token'],
            },
        )

        # Reload the secrets after getting the token.
        await self.load_secrets()

        return new_data

    def __repr__(self) -> str:
        return '<Auth object>'

    def __str__(self) -> str:
        return '<Auth object>'
