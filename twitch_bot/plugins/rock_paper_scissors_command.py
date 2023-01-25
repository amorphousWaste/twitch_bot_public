"""Rock, Paper, Scissors plugin."""

import random

from plugins._base_plugins import BaseCommandPlugin


class RockPaperScissors(BaseCommandPlugin):
    """Rock, Paper, Scissors plugin."""

    COMMAND = 'rps'

    async def run(self) -> None:
        """About the bot."""
        if not self.command_args:
            return -1

        options = ['rock', 'paper', 'scissors']
        bot_throw = options[random.randint(0, 2)]
        user_throw = self.command_args[0].lower()

        if user_throw not in options:
            await self.send_message(
                'You can only throw: {}'.format(', '.join(options))
            )
            return -1

        message = f'I throw {bot_throw}... '

        if bot_throw == user_throw:
            message += 'It\'s a tie.'

        elif (
            (bot_throw == 'rock' and user_throw == 'scissors')
            or (bot_throw == 'paper' and user_throw == 'rock')
            or (bot_throw == 'scissors' and user_throw == 'paper')
        ):
            message += 'I win!'

        else:
            message += 'You win!'

        await self.send_message(message)
