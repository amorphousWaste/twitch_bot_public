"""8Ball plugin."""

import random

from plugins._base_plugins import BaseCommandPlugin


class EightBallCommand(BaseCommandPlugin):
    """8Ball plugin."""

    COMMAND = '8ball'

    async def run(self) -> None:
        """Generic 8-ball."""
        if not self.command_args:
            await self.send_message('You need to ask a yes/no question.')
            return -1

        options = [
            'It is certain.',
            'It is decidedly so.',
            'Without a doubt.',
            'Yes definitely.',
            'You may rely on it.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Yes.',
            'Signs point to yes.',
            'Reply hazy, try again.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Concentrate and ask again.',
            'Don\'t count on it.',
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.',
        ]

        chosen_option = options[random.randint(0, len(options) - 1)]
        await self.send_message(f'The Magic 8 Ball says: {chosen_option}')
