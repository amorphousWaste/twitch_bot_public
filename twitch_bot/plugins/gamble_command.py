"""Gamble plugin."""

import random

from plugins._base_plugins import BaseCommandPlugin


class GambleCommand(BaseCommandPlugin):
    """Fake gambling for imaginary points."""

    COMMAND = 'gamble'
    USER_TIMEOUT = 5

    async def run(self) -> None:
        """Gamble plugin.

        Gamble some amount of useless points for more or less useless points.
        """
        # Get the waged points.
        if not self.command_args:
            await self.send_message('You need to specify points to gamble.')
            return -1

        # Get the database data for the user.
        db_data = dict(
            await self.db.read('users', queries={'user_id': self.user['id']})
        )
        current_points = int(db_data['points'])

        if current_points <= 0:
            await self.send_message(
                'Looks like you have no points. Take these 100 and have fun!'
            )
            current_points = 100

        if self.command_args[0] == 'all':
            waged_points = current_points
        else:
            try:
                waged_points = int(self.command_args[0])
            except ValueError:
                await self.send_message(
                    'You need to bet a number of points or all.'
                )
                return -1

        if waged_points > current_points:
            await self.send_message(f'You only have {current_points}.')
            return -1

        value = random.randint(0, 1)

        if value == 0:
            current_points -= waged_points
            await self.send_message(
                f'Sorry you lost {waged_points}'
                f' and now have {current_points} points.'
            )
        else:
            current_points += waged_points
            await self.send_message(
                f'Congratulations! You won {waged_points}'
                f' and now have {current_points} points.'
            )

        await self.db.update(
            'users', {'points': current_points}, {'user_id': self.user['id']}
        )
