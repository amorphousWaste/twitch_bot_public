"""Points plugin."""

from plugins._base_plugins import BaseCommandPlugin


class PointsCommand(BaseCommandPlugin):
    """Check imaginary points."""

    COMMAND = 'points'

    async def run(self) -> None:
        """Points plugin.

        Check how many points a user has.
        """
        # Get the database data for the user.
        db_data = dict(
            await self.db.read('users', queries={'user_id': self.user['id']})
        )
        current_points = int(db_data['points'])

        await self.send_message(f'You have {current_points} points.')
