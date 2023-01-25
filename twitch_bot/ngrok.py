"""Run ngrok."""

# import asyncio
import json
import os
import platform
import requests
import subprocess
import threading

from configs import config_utils
from log import LOG


class Ngrok(object):
    """Ngrok class."""

    def __init__(self) -> None:
        """Init."""
        super(Ngrok, self).__init__()

    async def init(self) -> object:
        """Async init."""
        config = await config_utils.load_config_file('bot_config')

        # Get ngrok data from the ngrok config
        self.ngrok_path = os.path.expanduser(config.get('ngrok_path'))
        # Add the exe extension for Windows
        if platform.system == 'Windows':
            self.ngrok_path += '.exe'

        self.ngrok_local_url = config.get('ngrok_local_url')

        # Get the port from the eventsub config
        bot_config = await config_utils.load_config_file('bot_config')
        self.ngrok_port = bot_config.get('eventsub_port')

        return self

    async def get_thread(self):
        """Get the ngrok service as a thread.

        Returns:
            ngrok_thread (Thread): Thread for running the ngrok process.
        """
        # Run the ngrok executable via subprocess.
        # 5000 is the default Flask port
        cmd = [
            self.ngrok_path,
            'http',
            '-host-header=rewrite',
            'https://127.0.0.1:5000',
        ]
        ngrok_thread = threading.Thread(
            target=lambda: subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            ),
            daemon=True,
        )

        # Possible future attempt at an async subprocess instead of a
        # threaded one.
        # ngrok_process = await asyncio.create_subprocess_shell(
        #     cmd,
        #     stdout=asyncio.subprocess.DEVNULL,
        #     stderr=asyncio.subprocess.DEVNULL,
        # )

        # await ngrok_process.wait()

        LOG.info(f'Info available at {self.ngrok_local_url}.')

        return ngrok_thread


async def get_url() -> str:
    """Return the generated ngrok url.

    Returns:
        ngrok_url (str): URL to pass to Twitch webhook subscriptions.
    """
    config = await config_utils.load_config_file('bot_config')
    ngrok_local_url = config.get('ngrok_local_url')
    ngrok_tunnel_data = config.get('ngrok_tunnel_data')

    url = ngrok_local_url + ngrok_tunnel_data

    try:
        data = requests.get(url).text
    except ConnectionError:
        LOG.warning('ngrok is not running.')
        return ''

    # Get the data from the local tunnel
    # This assumes a single tunnel.
    public_url = ''
    local_ngrok_data = json.loads(data)
    tunnels = local_ngrok_data.get('tunnels', [])
    for tunnel in tunnels:
        if tunnel['proto'] != 'https':
            continue

        public_url = tunnel['public_url']
        break

    if not public_url:
        LOG.error('A error occured running ngrok: service unavailable.')

    return public_url


async def is_static() -> bool:
    """Return whether or not the ngrok tunnel is static.

    Returns:
        (bool): True if static, False otherwise.
    """
    config = await config_utils.load_config_file('bot_config')
    return config.get('is_static', False)
