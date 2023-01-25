"""slots plugin."""

from random import randint

from plugins._base_plugins import BaseCommandPlugin


class SlotsCommand(BaseCommandPlugin):
    """Slots plugin."""

    COMMAND = 'slots'

    async def run(self) -> None:
        """Slots game with emotes."""
        user_emote_list = sorted(self.bot.emotes.get('user', {}).keys())
        total_user_emotes = len(user_emote_list)

        emote_1 = user_emote_list[randint(0, total_user_emotes - 1)]
        emote_2 = user_emote_list[randint(0, total_user_emotes - 1)]
        emote_3 = user_emote_list[randint(0, total_user_emotes - 1)]
        await self.send_message(f'{emote_1} {emote_2} {emote_3}')

        if emote_1 == emote_2 == emote_3:
            message = 'You win!'
        else:
            message = 'Sorry, you lose.'

        await self.send_message(f'{message}')
