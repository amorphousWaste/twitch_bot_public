"""How Am I plugin."""


from plugins._base_plugins import BaseCommandPlugin
from system import system_utils


class HowAmI(BaseCommandPlugin):
    """Respond to the question of how I'm doing."""

    COMMAND = 'howami'

    async def run(self) -> None:
        """How is the bot doing today."""
        message = []

        temp = await system_utils.get_cpu_temp()
        if temp > 0.0:
            message.append(f'I\'m running at {temp}C.')

        process_count = await system_utils.get_number_of_processes()
        message.append(
            f'I\'m one of {process_count} process currently running.'
        )

        disk_space_dict = await system_utils.get_disk_space()
        disk_space_percentage = disk_space_dict.get('percent', 0)
        if disk_space_percentage > 0:
            message.append(
                f'I\'m using {disk_space_percentage}% of my disk space.'
            )

        available_ram_dict = await system_utils.get_memory_info()
        available_ram = available_ram_dict.get('percent', 0)
        if available_ram > 0:
            message.append(f'I have {available_ram}% of my RAM available.')

        if not message:
            message.append('I\'m doing ok... I think...')

        await self.send_message(' '.join(message))
