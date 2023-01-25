"""EventSub Server."""

import cryptography  # noqa: Unused, but needed for adhoc ssl_context
import flask
import hashlib
import hmac
import threading
import traceback

from datetime import datetime

from configs import config_utils
from eventsub import eventsub_events
from init import CACHE, EVENT_QUEUE
from log import LOG

APP = flask.Flask(__name__)


async def check_request(request: flask.request) -> bool:
    """Check if the message from Twitch is valid and a special event.

    It may be a challenge or error message in addition to an event.

    Args:
        request (flask.request): Message to be sent.
    """
    # Check if the message was recieved within 10 minutes of creation.
    is_timely = await is_message_timely(request)
    if not is_timely:
        LOG.error('Message not timely.')
        return flask.Response(status=200)

    # Check if the message contains the proper secret.
    is_secure = await is_message_secure(request)
    if not is_secure:
        LOG.error('Message secret does not match.')
        return flask.Response(status=404)

    is_unique = await is_message_unique(request)
    if not is_unique:
        LOG.error('Message id is not unique.')
        return flask.Response(status=200)

    headers = request.headers
    notification_type = headers.get('Twitch-Eventsub-Message-Type')

    # If Twitch challenges the subscription,
    # reply with the given challenge.
    if notification_type == 'webhook_callback_verification':
        LOG.info('Challenge received.')
        return await challenge(request)

    # If a revocation message is received, reply with a 2XX status.
    if notification_type == 'revocation':
        LOG.error('Subscription revoked.')
        return await error_reply()


async def is_message_timely(request: flask.request) -> bool:
    """Check if the message is timely based on time sent.

    Args:
        request (flask.request): Message to be sent.

    Returns:
        (bool): True if the message is timely, False otherwise.
    """
    message = request.json
    created_at_str = message.get('subscription', {}).get('created_at', '')
    if not created_at_str:
        return False

    try:
        created_at = datetime.strptime(
            created_at_str.split('.')[0], '%Y-%m-%dT%H:%M:%S'
        )
    except ValueError:
        LOG.error(
            'Unable to convert created at time to timestamp: {created_at}.'
        )
        return False

    now = datetime.now()
    # Time since message was sent in minutes.
    delta = (now - created_at).total_seconds() / 60
    # Twitch recommends ignoring messages older than 10 minutes.
    if delta > 10:
        LOG.warning('Non-timely message received: discarding.')
        return False

    return True


async def is_message_secure(request: flask.request) -> bool:
    """Check if the message is secure based on the secret.

    Args:
        request (flask.request): Message to be sent.

    Returns:
        (bool): True if the message is secure, False otherwise.
    """
    twitch_secrets = await config_utils.load_config_file('secrets')
    eventsub_secret = twitch_secrets.get('eventsub_secret')

    message_signature = request.headers.get(
        'twitch-eventsub-message-signature'
    )

    if not message_signature:
        LOG.warning('Message has no signature, cannot confirm authenticity.')
        return True

    hmac_message = '{}{}{}'.format(
        request.headers.get('twitch-eventsub-message-id'),
        request.headers.get('twitch-eventsub-message-timestamp'),
        request.get_data(as_text=True),
    )

    key = bytes(eventsub_secret, 'utf-8')
    data = bytes(hmac_message, 'utf-8')
    expected_signature = (
        'sha256=' + hmac.new(key, data, hashlib.sha256).hexdigest()
    )

    if message_signature != expected_signature:
        LOG.warning('Insecure message received: discarding.')
        return False

    return True


async def is_message_unique(request: flask.request) -> bool:
    """Check if the message is unique based on id.

    Args:
        request (flask.request): Message to be sent.

    Returns:
        (bool): True if the message is unique, False otherwise.
    """
    message_id = request.headers.get('twitch-eventsub-message-id')
    if await CACHE.exists(message_id):
        LOG.warning('Non-unique message received: discarding.')
        return False

    await CACHE.add(key=message_id, data=request, duration=10)
    return True


async def challenge(request: flask.request) -> flask.Response:
    """Create a challenge response when Twitch requests one.

    The response should be the challenge value as plain text.

    Args:
        request (flask.request): Message to be sent.

    Returns:
        response (flask.Response): Response to the challenge.
    """
    message = request.json
    challenge = message.get('challenge', '')
    LOG.info(f'challenge: {challenge}')
    if not challenge:
        LOG.error('Challenge not found.')
        return

    response = flask.make_response(challenge)
    response.mimetype = 'text/plain'
    return response


async def error_reply() -> flask.Response:
    """Reply to 'bad' messages with '200' as required.

    Returns:
        response (flask.Response): Response to the challenge.
    """
    response = flask.make_response('', 200)
    response.mimetype = 'text/plain'
    return response


@APP.route('/')
async def index() -> flask.Response:
    """Default page at root.

    Returns:
        (flask.Response): Response to the challenge.
    """
    return flask.Response(status=200)


@APP.route('/auth')
async def authorize() -> flask.Response:
    """Authenticate via OAuth process.

    Returns:
        (flask.Response): Response to the challenge.
    """
    LOG.debug(flask.request.json)
    return flask.Response(status=200)


@APP.route('/events', methods=['POST'])
async def process_event() -> flask.Response:
    """Process webhooks for eventsub events.

    Returns:
        (flask.Response): 200 indicating a success.
    """
    response = await check_request(flask.request)
    if response:
        return response

    message = flask.request.json
    subscription_type = message.get('subscription', {}).get('type', '')
    LOG.debug(f'{subscription_type} event received: {message}')

    subscription_mapping = {
        'channel.follow': eventsub_events.FollowEvent,
        'channel.subscribe': eventsub_events.SubscribeEvent,
        'channel.subscription.gift': eventsub_events.SubscriptionGiftEvent,
        'channel.subscription.message': (
            eventsub_events.SubscriptionMessageEvent
        ),
        'channel.cheer': eventsub_events.CheerEvent,
        'channel.raid': eventsub_events.RaidEvent,
        'channel.channel_points_custom_reward_redemption.add': (
            eventsub_events.RewardRedemptionEvent
        ),
        'channel.channel_points_custom_reward_redemption.update': (
            eventsub_events.RewardRedemptionUpdateEvent
        ),
        'channel.goal.end': eventsub_events.GoalEndEvent,
        'channel.hype_train.begin': eventsub_events.HypeTrainBeginEvent,
        'channel.hype_train.progress': eventsub_events.HypeTrainProgressEvent,
        'channel.hype_train.end': eventsub_events.HypeTrainEndEvent,
        'channel.update': eventsub_events.ChannelUpdate,
        'stream.online': eventsub_events.StreamOnlineEvent,
        'stream.offline': eventsub_events.StreamOfflineEvent,
    }

    event = subscription_mapping.get(subscription_type, '')
    if not event:
        LOG.warning(f'No subscrition event matches {subscription_type}')
        return flask.Response(status=200)

    LOG.debug(f'Making {event}')

    try:
        await EVENT_QUEUE.put(await event().init(message))
    except Exception as e:
        LOG.error(
            'Error creating : {} event: {}'.format(
                subscription_type,
                getattr(e, 'message', repr(e)),
            )
        )
        traceback.print_exc()

    return flask.Response(status=200)


async def get_thread() -> None:
    """Get the Flask server thread to receive EventSub messages.

    Returns:
        flask_thread (Thread): Flask server thread.
    """
    # Run the Flask server in its own thread.
    flask_thread = threading.Thread(
        target=lambda: APP.run(
            debug=True if LOG.level == 0 else False,
            use_reloader=False,
            ssl_context='adhoc',
        ),
        daemon=True,
    )

    return flask_thread
