"""Spells plugin."""

from init import CACHE
from plugins._base_plugins import BaseCommandPlugin


class PowerpuffCommand(BaseCommandPlugin):
    """Powerpuff plugin."""

    COMMAND = 'powerpuff'
    ALLOWED = ['bot']

    async def run(self) -> None:
        """Make the Powerpuff Girls."""
        if not await CACHE.exists('powerpuff'):
            await CACHE.add('powerpuff', data={'components': [], 'users': []})

        potion = await CACHE.get('powerpuff')
        if self.user['name'] in potion.data['users'] or not self.bot.owner:
            await self.send_message('You already added a component.')
            return -1

        component = self.command_args[0]
        if component in potion.data['components']:
            await self.send_message('That component has already been added.')
            return -1

        potion.data['users'].append(self.user['name'])
        potion.data['components'].append(component)
        potion.data['users'].sort()
        potion.data['components'].sort()

        self.send_message(f'{component} has been added.')

        needed_components = ['chemical x', 'everything nice', 'spice', 'sugar']
        needed_components.sort()

        if not potion.data['components'] == needed_components:
            return

        await self.send_message('Thus the Powerpuff Girls were born!')
        potion.data = {'components': [], 'users': []}


class MagicMissileCommand(BaseCommandPlugin):
    """Magic Missile plugin."""

    COMMAND = 'magicmissile'
    ALLOWED = ['bot']

    async def run(self) -> None:
        """Magic Missile."""
        await self.bot.obs.show_source('pew')
        await self.send_message('Pew Pew Pew')
