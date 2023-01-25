"""Hotkey triggering module."""

from pynput.keyboard import Key, Controller

from configs import config_utils
from log import LOG


class Hotkeys(object):
    """Hotkey triggering class."""

    def __init__(self) -> None:
        """Init."""
        super(Hotkeys, self).__init__()

    async def init(self) -> object:
        """Async init.

        Returns:
            self (object): self
        """
        await self.reload_hotkeys()
        self.keyboard = Controller()
        return self

    async def reload_hotkeys(self) -> None:
        """Reload the hotkey definition file."""
        self.hotkeys = await config_utils.load_config_file('hotkeys')

    async def check(self, command: str) -> None:
        """Ensure the hotkey command exists.

        Args:
            command (str): Command to run the hotkey for.
        """
        return command in self.hotkeys

    async def trigger(self, command: str) -> None:
        """Trigger the hotkey based on the given command.

        Args:
            command (str): Command to run the hotkey for.
        """
        LOG.debug(f'Triggering {command} hotkey: {self.hotkeys[command]}.')
        # Build the key to trigger.
        to_press = []
        for keypress in self.hotkeys[command].split('+'):
            keypress = keypress.strip()

            # If the keypress is a special key, get it from pynput.
            if hasattr(Key, keypress):
                to_press.append(getattr(Key, keypress))

            # Otherwise, assume it is a simple keypress.
            else:
                to_press.append(str(keypress))

        try:
            # Press the keys in the given order.
            for key in to_press:
                self.keyboard.press(key)

            # Release the keys in reverse order.
            to_press.reverse()
            for key in to_press:
                self.keyboard.release(key)

        except Exception as e:
            LOG.error(
                'Hotkey command {} failed: {}'.format(
                    command, getattr(e, 'message', repr(e))
                )
            )
