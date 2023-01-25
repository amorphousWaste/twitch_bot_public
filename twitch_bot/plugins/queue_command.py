"""Queue plugins."""
from typing import Optional

from plugins._base_plugins import BaseCommandPlugin
from init import CACHE


class Queue(object):
    """Queue storage object.

    Queues are First-On / First-Off Stacks.
    """

    def __init__(self, name: Optional[str] = 'Queue') -> None:
        """Init.

        Args:
            name (str, optional): Name of the queue.
        """
        super(Queue, self).__init__()
        self.name = name
        self.open = True
        self.members = []

    async def reopen(self) -> None:
        """Reopen the queue."""
        self.open = True

    async def close(self) -> None:
        """Close the queue."""
        self.open = False

    async def add(self, member: str) -> None:
        """Add a member to the queue.

        Args:
            member (str): Member to add to the end of the queue.
        """
        self.members.append(member)

    async def remove(self, member: str) -> None:
        """Remove a member from the queue.

        Args:
            member (str): Member to remove from the queue.
        """
        if member in self.members:
            self.members.remove(member)

    @property
    async def current(self) -> str:
        """Show the current first position in the queue."""
        if self.members:
            return self.members[0]

    @property
    async def next_up(self) -> str:
        """Show who is next."""
        if len(self.members) > 1:
            return self.members[1]

    async def next(self) -> None:
        """Remove the current first member from the list."""
        if self.members:
            self.members.pop(0)

    @property
    async def is_open(self) -> bool:
        """Returns True if the queue is open, otherwise False."""
        return self.open


class QueueCommand(BaseCommandPlugin):
    """Queue plugin.

    Create a queue for users to enter.
    """

    ALLOWED = ['bot']
    COMMAND = 'queue'

    async def run(self) -> None:
        """Queue command."""
        if not await CACHE.exists('queue'):
            await CACHE.add('queue', Queue(), overwrite=False)
            await self.send_message('Queue has been created.')
            return

        queue = await CACHE.get('queue').data
        if not queue.is_open:
            await queue.reopen()
            await self.send_message('Queue has been reopened.')
            return


class ListQueueCommand(BaseCommandPlugin):
    """List queue plugin.

    Create a queue for users to enter.
    """

    ALLOWED = ['bot']
    COMMAND = 'list'

    async def run(self) -> None:
        """Queue command."""
        if not await CACHE.exists('queue'):
            return -1

        members = ', '.join(await CACHE.get('queue').data.members)
        if not members:
            await self.send_message('Queue is empty.')
        else:
            await self.send_message(f'Queue: {members}.')


class JoinQueueCommand(BaseCommandPlugin):
    """Join a queue."""

    COMMAND = 'join'

    async def run(self) -> None:
        """Join queue command."""
        if not await CACHE.exists('queue'):
            return -1

        queue = await CACHE.get('queue').data
        if not queue.is_open:
            await self.send_message('Queue is closed.')
            return -1

        username = self.user['name']

        if username not in queue.members:
            await queue.add(username)
            await self.send_message(
                '{} has been added to the queue.'.format(username)
            )
        else:
            await self.send_message(
                '{} is already in the queue.'.format(username)
            )
            return -1


class LeaveQueueCommand(BaseCommandPlugin):
    """Leave a queue."""

    COMMAND = 'leave'

    async def run(self) -> None:
        """Leave queue command."""
        if not await CACHE.exists('queue'):
            return -1

        queue = await CACHE.get('queue').data
        if self.user['name'] in queue.members:
            await queue.remove(self.user['name'])
            await self.send_message(
                '{} has left the queue.'.format(self.user['name'])
            )


class NextQueueCommand(BaseCommandPlugin):
    """Go to the next person in the queue."""

    ALLOWED = ['bot']
    COMMAND = 'next'

    async def run(self) -> None:
        """Next queue command."""
        if not await CACHE.exists('queue'):
            return -1

        queue = await CACHE.get('queue').data
        await queue.next()
        if await queue.current:
            await self.send_message('@{} is now up.'.format(queue.current))

        if await queue.next_up:
            await self.send_message('@{} is next.'.format(queue.next_up))


class CloseQueueCommand(BaseCommandPlugin):
    """Close the queue."""

    ALLOWED = ['bot']
    COMMAND = 'close'

    async def run(self) -> None:
        """Close queue command."""
        if not await CACHE.exists('queue'):
            return -1

        queue = await CACHE.get('queue').data
        if not queue.is_open:
            await self.send_message('Queue is already closed.')
            return -1

        await queue.close()
        await self.send_message('Queue is now closed.')
