"""Simple commands plugins."""

import re

from plugins._base_plugins import BaseCommandPlugin

COMMAND_PATTERN = re.compile(
    r'^(?P<task>add|edit|delete)\s!?(?P<name>\w+)'
    r'(?P<command_group>\s\"(?P<command>.+)\")?$'
)


class CommandsCommand(BaseCommandPlugin):
    """Create, modify, and/or delete simple commands plugin."""

    COMMAND = 'commands'
    ALLOW = ['mod']

    async def run(self) -> None:
        """Create, modify, and/or delete simple commands."""
        if not self.command_args:
            await self.send_message(
                'Please specify "add", "edit", or "delete", the command name, '
                'and the command inside quotes.'
            )
            return -1

        merged_args = ' '.join(self.command_args)
        match = re.match(COMMAND_PATTERN, merged_args)
        if not match:
            await self.send_message(
                'Please specify "add", "edit", or "delete", the command name, '
                'and the command inside quotes.'
            )
            return -1

        task, name, _, code = match.groups()

        if task == 'add':
            result = await self.bot.simple_commands.add_command(name, code)
            if result:
                await self.send_message(f'Command {name} successfully added.')

        elif task == 'edit':
            result = await self.bot.simple_commands.edit_command(name, code)
            if result:
                await self.send_message(f'Command {name} successfully edited.')

        elif task == 'delete':
            result = await self.bot.simple_commands.delete_command(name, code)
            if result:
                await self.send_message(
                    f'Command {name} successfully deleted.'
                )

        else:
            return -1
