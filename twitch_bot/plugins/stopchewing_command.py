"""Stop Chewing plugin."""

from plugins._base_plugins import BaseCommandPlugin


class StopChewing(BaseCommandPlugin):
    """Count every time I tell the bun to stop chewing on the carpet."""

    COMMAND = 'chew'

    async def run(self) -> None:
        """Stop chewing counter.

        Count how many times I have to tell my rabbit to stop chewing on my
        carpet.
        """
        counter = await self.db.count_rows(self.__class__.__name__) + 1
        await self.send_message(f'Stop chewing counter: {counter}')
