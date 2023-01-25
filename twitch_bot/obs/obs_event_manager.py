"""OBS Callback Event Manager."""

from typing import Callable

from log import LOG


class CallbackEvent(object):
    """Callback event."""

    def __init__(self):
        """Init."""
        super(CallbackEvent, self).__init__()

    async def init(self, callback: Callable, trigger: object) -> object:
        """Async init.

        Args:
            callback (Callable): Function to run on event received.
            trigger (Event): OBS event received.

        Returns:
            self (CallbackEvent): Class instance.
        """
        self.callback = callback
        self.trigger = trigger
        LOG.debug(f'Created: {self.callback} - {self.trigger}')

        return self


class CallbackEventManager(object):
    """Callback event manager."""

    def __init__(self):
        """Init."""
        super(CallbackEventManager, self).__init__()

        self.callbacks = []

    async def init(self) -> object:
        """Async init.

        Returns:
            self (CallbackEventManager): Class instance.
        """
        return self

    async def register(self, func: Callable, trigger: object) -> None:
        """Register a callback event.

        Args:
            func (Callable): Function to run on event received.
            trigger (Event): OBS event received.
        """
        LOG.debug(f'Registering: {trigger} -> {func}')
        callback = await CallbackEvent().init(func, trigger)
        self.callbacks.append(callback)

    async def unregister(self, callback: Callable, trigger: object) -> None:
        """Unregister a callback event.

        Args:
            callback (Callable): Function to run on event received.
            trigger (Event): OBS event received.
        """
        LOG.debug(f'Unregistering: {trigger} -> {callback}')
        for callback in self.callbacks:
            if callback.callback == callback and (
                trigger is None or callback.trigger == trigger
            ):
                self.callbacks.remove(callback)

    async def trigger(self, event: object) -> None:
        """Trigger the callbacks from the event.

        Args:
            event (event): OBS event.
        """
        LOG.debug(f'Triggering: {event}')
        for callback in self.callbacks:
            if callback.trigger is None or isinstance(event, callback.trigger):
                await callback.callback(event)
