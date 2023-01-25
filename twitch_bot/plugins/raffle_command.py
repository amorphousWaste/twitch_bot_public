"""Raffle plugin."""

from random import randint

from init import CACHE
from plugins._base_plugins import BaseCommandPlugin


class RaffleCommand(BaseCommandPlugin):
    """Raffle plugin."""

    COMMAND = 'raffle'
    ALLOWED = ['bot']

    async def run(self) -> None:
        """Manage a raffle."""
        if not self.command_args:
            await self.send_message(
                'Use "start" to start a raffle, "end" to close the entries, '
                'and "choose" to pick a winner.'
            )
            return -1

        if self.command_args[0] == 'start':
            if not await CACHE.exists('raffle'):
                await CACHE.add('raffle', data={'open': True, 'users': []})
                await self.send_message(
                    'The raffle has started. Use "!enter" to join.'
                )
                return

            else:
                await self.send_message('Raffle already underway.')
                return -1

        raffle = await CACHE.get('raffle')

        if self.command_args[0] == 'open':
            raffle.data['open'] = True
            await self.send_message('Raffle is open for entries.')
            return

        if self.command_args[0] == 'close':
            raffle.data['open'] = False
            await self.send_message('Raffle is closed.')
            return

        if self.command_args[0] == 'choose':
            if raffle.data['open']:
                await self.send_message(
                    'Raffle is still open. '
                    'Please close it before choosing a winner.'
                )
                return -1

            users = raffle.data['users']
            if not users:
                await self.send_message(
                    'The raffle has no entries, nobody wins.'
                )
                return

            winning_index = randint(0, len(users) - 1)
            winner = users[winning_index]
            await self.send_message(
                f'The winner of the raffle is: {winner}! Congrats!'
            )
            return


class EnterRaffleCommand(BaseCommandPlugin):
    """Enter raffle plugin."""

    COMMAND = 'enter'

    async def run(self) -> None:
        """Enter an ongoing raffle."""
        if not await CACHE.exists('raffle'):
            await self.send_message('There are no raffles at this time.')
            return -1

        raffle = await CACHE.get('raffle')

        if raffle.data['open'] is False:
            await self.send_message(
                'The raffle is closed to additional entries.'
            )
            return -1

        username = self.user['name']
        users = raffle.data['users']
        if username not in users:
            users.append(username)
            await self.send_message(f'{username} has entered the raffle.')

        else:
            await self.send_message(
                f'{username} has already entered the raffle.'
            )
            return -1


class ExitRaffleCommand(BaseCommandPlugin):
    """Exit raffle plugin."""

    COMMAND = 'exit'

    async def run(self) -> None:
        """Exit an ongoing raffle."""
        if not await CACHE.exists('raffle'):
            await self.send_message('There are no raffles at this time.')
            return -1

        raffle = await CACHE.get('raffle')

        if raffle.data['open'] is False:
            await self.send_message('The raffle is closed.')
            return -1

        username = self.user['name']
        users = raffle.data['users']
        if username in users:
            users.remove(username)
            await self.send_message(f'{username} has exited the raffle.')

        else:
            await self.send_message(f'{username} has not entered the raffle.')
            return -1
