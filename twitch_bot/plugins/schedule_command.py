"""Schedule plugin."""

import api
import utils

from plugins._base_plugins import BaseCommandPlugin


class ScheduleCommand(BaseCommandPlugin):
    """Schedule plugin.

    Get and print the schedule for the next few streams.
    """

    COMMAND = 'schedule'

    async def run(self) -> None:
        """Show the schedule."""
        data = await api.get_schedule(self.bot.auth)

        # Check if the streamer is on vacation.
        vacation = data.get('vacation', None)
        if vacation:
            # Parse the datetime from Twitch.
            vacation_start = await utils.parse_datetime(
                vacation.get('start_time', '')
            )
            formatted_vacation_start = (
                f'{vacation_start.year}-{vacation_start.month}-'
                f'{vacation_start.date}'
            )

            # Parse the datetime from Twitch.
            vacation_end = await utils.parse_datetime(
                vacation.get('end_time', '')
            )
            formatted_vacation_end = (
                f'{vacation_end.year}-{vacation_end.month}-'
                f'{vacation_end.date}'
            )

            await self.send_message(
                'Stream will be on vacation from '
                f'{formatted_vacation_start} to {formatted_vacation_end}.'
            )
            return

        # No segments in the data means nothing in the schedule.
        segments = data.get('segments', [])
        if not segments:
            await self.send_message('No future streams planned.')
            return

        msg = []
        for segment in segments:
            # Parse the datetime from Twitch.
            start = await utils.parse_datetime(segment.get('start_time', ''))
            msg.append(
                f'{start.year}-{start.month}-{start.day} '
                f'at {start.hour}:{start.minute:02}'
            )

        await self.send_message(
            'The next streams are: {}.'.format(', '.join(msg))
        )
