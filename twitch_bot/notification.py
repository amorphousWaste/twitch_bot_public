"""System notification sender."""

import os
import platform

from typing import Optional

from log import LOG


async def notify(
    message: str,
    subtitle: Optional[str] = 'An error occured.',
    caller: Optional[str] = 'TwitchBot',
) -> None:
    """Send a system notification based on the OS."""
    system = platform.system()
    icon_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'images', 'icon.png'
    )

    # macOS
    if system == 'Darwin':
        cmd = (
            f'osascript -e \'display notification "{message}" with title '
            f'"{caller}" subtitle "{subtitle}"\''
        )
        os.system(cmd)

    # Linux
    elif system == 'Linux':
        cmd = f'notify-send "{caller}" "{message}"'
        os.system(cmd)

    # Windows
    elif system == 'Windows':
        from winotify import Notification

        toast = Notification(
            app_id=caller,
            title=caller,
            msg=message,
            icon=icon_path,
        )
        toast.show()

    else:
        LOG.warning(f'Unknown system: {system}; cannot send notification.')
