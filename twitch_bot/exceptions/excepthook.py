"""Bot exception handler."""

import asyncio
import traceback

import notification

from configs import config_utils
from log import LOG


def handler(error_type: Exception, value: str, tb: traceback) -> None:
    """Excepthook override for uncaught exception handling.

    Args:
        error_type (Exception): Type of exception.
        value (str): Error message.
        traceback (traceback): Traceback object.
    """
    LOG.error('An unhandled exception occured:')
    traceback.print_exception(error_type, value, tb)

    config = asyncio.run(config_utils.load_config_file('bot_config'))
    if config.get('desktop_notification', True):
        asyncio.run(
            notification.notify('The bot crashed. You should have a look.')
        )
