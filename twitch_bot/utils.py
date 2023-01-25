"""Utilities."""

import math
import os
import traceback

from datetime import datetime, timedelta
from matplotlib import pyplot

import api

from configs import config_utils
from log import LOG


async def parse_datetime(datetime_string: str) -> datetime:
    """Parse a datetime string from the Twitch message into a datetime object.

    If the datetime cannot be parsed, it will return the current time.

    Args:
        datetime_string (str): Datetime string.

    Returns:
        datetime.datetime: Datetime in an object.
    """
    config = await config_utils.load_config_file('bot_config')
    datetime_string = datetime_string.rstrip('Z')

    # Determine the format.
    if ' ' in datetime_string:
        datetime_format = '%Y-%m-%d %H:%M:%S'
    else:
        datetime_format = "%Y-%m-%dT%H:%M:%S"

    try:
        # The split is done to ignore milliseconds if present.
        parsed_dt = datetime.strptime(
            datetime_string.split('.')[0], datetime_format
        )

        # Times are given in GMT so offset the timezone by the offset.
        timezone_offset = timedelta(hours=config.get('timezone_offset', 0))
        dt = parsed_dt + timezone_offset

    except (ValueError, IndexError):
        LOG.error(
            f'datetime_string is in an unknown format {datetime_string}.'
        )
        dt = datetime.now()

    except Exception:
        LOG.error(f'An unknown problem occured parsing {datetime_string}.')
        traceback.print_exc()
        dt = datetime.now()

    return dt


async def get_viewer_count(bot: object) -> int:
    """Get the current viewer count.

    Args:
        bot (TwitchBot): The bot instance.

    Returns:
        (int): Current viewer count.
    """
    data = await api.get_stream_data(bot.auth, bot.broadcaster_id)
    if not data:
        return 0

    return data[0].get('viewer_count', 0)


async def get_follow_age(user_id: str, bot: object) -> str:
    """Get the length of time a user has been following.

    Args:
        user_id (str): Twitch user ID.
        bot (TwitchBot): The bot instance.

    Returns:
        display_time (str): Length of time as a string.
    """
    follow_data = await api.get_follow_data(
        bot.auth, user_id, bot.broadcaster_id
    )
    if not follow_data:
        return

    LOG.debug(follow_data)

    now = datetime.now()
    followed_at = await parse_datetime(follow_data.get('followed_at'))
    seconds = (now - followed_at).total_seconds()

    display_time = await display_from_seconds(seconds)
    return display_time


async def display_from_seconds(seconds: int) -> str:
    """Convert seconds to larger time intervals.

    Args:
        seconds (int): Time in seconds.

    Returns:
        (str): Time string.
    """
    intervals = (
        ('years', 31449600),
        ('months', 2620800),
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )

    result = []

    for name, count in intervals:
        value = seconds // count

        if value:
            seconds -= value * count
            value = int(value)

            if value == 1:
                name = name.rstrip('s')

            result.append(f'{value} {name}')

    return ', '.join(result)


async def get_uptime(bot: object) -> str:
    """Get how long a stream has been running.

    Args:
        bot (TwitchBot): The bot instance.

    Returns:
        (str): How long the stream has been running.
    """
    channel_data = await api.get_channel_data(
        bot.auth, bot.connection.channel.lstrip('#')
    )
    started_at_string = channel_data.get('started_at', '')
    if not started_at_string:
        return 0

    started_at = await parse_datetime(started_at_string)
    now = datetime.now()
    delta = now - started_at
    seconds = int(delta.total_seconds())

    return await display_from_seconds(seconds)


async def get_watch_time(bot: object, user: dict) -> str:
    """Get how long a user has been watching the stream.

    Args:
        bot (TwitchBot): The bot instance.
        user (dict): User that sent the message.
                {name: display name, id: user-id}

    Returns:
        (str): How long the user has been watching the stream.
    """
    user_db_data = dict(
        await bot.db.read(table='users', queries={'username': user['name']})
    )

    join_time = datetime.fromisoformat(user_db_data['last_join_time'])
    now = datetime.now()
    delta = now - join_time
    seconds = int(delta.total_seconds())

    return await display_from_seconds(seconds)


async def graph_stream_stats(bot: object) -> None:
    """Graph the stream stats.

    Args:
        bot (TwitchBot): The bot instance.
    """
    stats_last_row = dict(await bot.db.get_last_row('stream_stats'))
    stream_start = datetime.fromisoformat(stats_last_row.get('stream_start'))
    stream_end = datetime.fromisoformat(stats_last_row.get('stream_end'))

    data = await bot.db.read_range(
        'viewer_count',
        ranges=[
            {
                'key': 'date',
                'start': str(stream_start.date()),
                'end': str(stream_end.date()),
            }
        ],
    )

    x_values = []
    y_values = []
    count = 1
    for row in data:
        row_data = dict(row)
        x_values.append(str(datetime.fromisoformat(row_data.get('last_run'))))
        y_values.append(int(row_data.get('viewer_count')))
        count += 1

    # if not values['time'] or not values['viewer_count']:
    if not x_values or not y_values:
        LOG.warning('No data to graph.')
        return

    font_dict = {
        'family': 'sans-serif',
        'color': 'black',
        'weight': 'normal',
        'size': 12,
    }

    graph_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'stream_stats',
    )

    pyplot.figure(figsize=(20, 6), tight_layout=True, dpi=100)
    pyplot.plot(
        x_values, y_values, color='purple', linestyle='solid', linewidth=1
    )
    pyplot.title('Viewer Stats', fontdict=font_dict)
    pyplot.xlabel('Time', fontdict=font_dict)
    pyplot.ylabel('Viewer Count', fontdict=font_dict)
    pyplot.xticks(rotation=45, horizontalalignment='center', alpha=0.7)
    pyplot.yticks(
        range(math.floor(min(y_values)), math.ceil(max(y_values)) + 1)
    )
    pyplot.grid(
        color='black', linestyle='--', linewidth=0.5, axis='both', alpha=0.1
    )

    pyplot.gca().spines['top'].set_alpha(0.0)
    pyplot.gca().spines['bottom'].set_alpha(0.3)
    pyplot.gca().spines['right'].set_alpha(0.0)
    pyplot.gca().spines['left'].set_alpha(0.3)

    pyplot.savefig(
        os.path.join(
            graph_path, 'viewer_count_{}.png'.format(stream_start.date())
        ),
        dpi=100,
    )

    LOG.debug(x_values)
    LOG.debug(y_values)


async def generate_stats_markdown(bot: object) -> None:
    """Generate a markdown document with the stream stats.

    Args:
        bot (TwitchBot): The bot instance.
    """
    stats_last_row = dict(await bot.db.get_last_row('stream_stats'))
    stream_start = stats_last_row.get('stream_start')
    stream_date = stream_start.split(' ')[0]

    doc = [f'# Stream Stats for {stream_date} #']
    doc.append('## Viewer Count ##')
    doc.append(f'![stats](viewer_count_{stream_date}.png)')
    doc.append('## Interactions ##')
    for item in sorted(stats_last_row):
        if item in ['id', 'stream_end', 'stream_start']:
            continue

        doc.append(f'-   **{item}**: {stats_last_row[item]}')

    doc_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'stream_stats',
        f'stream_stats_{stream_date}.md',
    )

    with open(doc_path, 'w') as out_file:
        out_file.write('\n'.join(doc))
