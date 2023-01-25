"""Audio utilities."""

import os
import traceback

from playsound import playsound

from configs import config_utils
from log import LOG


async def play(name: str) -> None:
    """Play an audio file given its name.

    Args:
        name (str): Name of the audio file to play.
    """
    config = await config_utils.load_config_file('bot_config')
    audio_folder = config.get('audio_folder', None) or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'audio'
    )

    audio_path = os.path.join(audio_folder, f'{name}.mp3')
    if os.path.exists(audio_path):
        try:
            playsound(audio_path)
        except Exception as e:
            LOG.error(
                f'Unable to play audio file: {audio_path}'.format(
                    getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()
