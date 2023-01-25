"""Pancake plugin."""

from tortoise import fields

# from plugins._base_plugins import BaseCommandPlugin
from plugins._base_model import AbstractPluginModel


class PancakeModel(AbstractPluginModel):
    stack = fields.IntField(default=0)

    class Meta:
        table = 'PancakeCommand'


class PancakeCommand(object):
    """Pancake plugin.

    A game where people can stack pancakes for a stream.
    Rules:
        1. Anyone can use the !pancake command.
        2. Once a person uses the command, they must wait until someone else
            uses it.
        3. The command has a small timeout to prevent multiple people from
            spamming the command back and forth.
    """

    COMMAND = 'pancake'
    FIELDS = {'stack': 'INT DEFAULT 0'}
    RESET = {'stack': 0}
    TIMEOUT = 5

    async def run(self) -> dict:
        """Pancake game."""
        # If there is no data, the stack is created as a normal DB entry
        if not self.last_row:
            return {'stack': 1}

        row_dict = dict(self.last_row)
        current_stack = row_dict.get('stack')

        if int(self.user.get('id')) == int(row_dict.get('last_user_id')):
            user_name = self.user.get('name')
            await self.send_message(
                f'{user_name} cannot add to the stack until someone else does.'
            )
            return -1

        new_stack = current_stack + 1
        await self.send_message(
            f'PANCAKEBUNNY There are now {new_stack} pancakes on the stack! '
            'PANCAKEBUNNY'
        )

        return {'stack': new_stack}
