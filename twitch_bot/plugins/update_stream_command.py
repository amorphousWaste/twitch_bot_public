"""Update stream information plugin."""

import api

from plugins._base_plugins import BaseCommandPlugin


class UpdateStreamCommand(BaseCommandPlugin):
    """Update stream information plugin."""

    ALLOWED = ['bot']
    COMMAND = 'stream'

    async def run(self) -> None:
        """Update stream information."""
        if not self.command_args:
            await self.send_message(
                'You need to specify whether to change: "title" or "game" '
                'and provide the information.'
            )
            return -1

        if len(self.command_args) < 2:
            await self.send_message(
                'You need to specify whether to change: "title" or "game" '
                'and provide the information.'
            )
            return -1

        option = self.command_args[0]
        update_info = ' '.join([u.strip('"') for u in self.command_args[1:]])

        if option == 'title':
            patch = {'title': update_info}

        elif option == 'game':
            game_data = await api.get_game(
                self.bot.auth, game_name=update_info
            )

            if not game_data:
                await self.send_message(f'Unknown game: {update_info}.')
                return -1

            patch = {'game_id': game_data.get('id')}

        else:
            await self.send_message(
                f'Unknown option {option}. Options are "title" or "game".'
            )
            return -1

        await api.update_stream_settings(self.bot.auth, patch)
