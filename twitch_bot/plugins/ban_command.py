"""Ban plugin."""

from plugins._base_plugins import BaseCommandPlugin


class BanCommand(BaseCommandPlugin):
    """Ban plugin.

    Used when people jokingly ban a person.
    """

    COMMAND = 'ban'

    async def run(self) -> None:
        """Joke ban command."""
        if not self.command_args:
            await self.send_message(
                'You need to specify the person you are pretending to ban.'
            )
            return -1

        names = [n.lstrip('@').lower() for n in self.command_args]
        if self.bot.owner.lower() in names:
            await self.send_message('You wish.')

        elif self.user['name'].lower() in names:
            await self.send_message(
                'Imagine if I actually let you ban yourself.'
            )

        elif self.bot.username.lower() in names:
            await self.send_message('from revenge import cold_dish')

        else:
            await self.send_message('Yeah, I\'ll get right on that.')
