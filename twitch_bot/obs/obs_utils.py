"""Library for working with OBS."""

import traceback

from typing import Callable

from log import LOG
from obs import obs_requests


class OBS(object):
    """OBS object."""

    def __init__(self) -> None:
        """Init."""
        super(OBS, self).__init__()

    async def init(self, obs_connection: object) -> None:
        """Async init.

        Args:
            obs_connection (OBSConnection): Connection object to OBS.

        Returns:
            self (OBS): Class instance.
        """
        self.obs_connection = obs_connection
        await self.obs_connection.register(self.on_event)

        return self

    def check_connection(func: Callable) -> None:
        """Decorator to check the connection to OBS.

        Args:
            func (Callable): Decorated function.

        Returns:
            (Any): Result of the decorated function.
        """

        async def wrapper(self, value: str) -> None:
            """Wrapped function."""
            if self.obs_connection.connected:
                await func(self, value)

            else:
                LOG.error(f'OBS is not connected, cannot run: {func}')

        return wrapper

    @check_connection
    async def change_scene(self, scene_name: str) -> None:
        """Change the OBS scene.

        Args:
            scene_name (str): Name of the scene to change to.
        """
        scenes = self.obs_connection.call(obs_requests.GetSceneList())
        if scene_name not in scenes.getScenes():
            LOG.error(f'Scene: {scene_name} does not exist.')
            return

        LOG.debug(f'Switching to {scene_name}')
        try:
            self.obs_connection.call(obs_requests.SetCurrentScene(scene_name))

        except Exception as e:
            LOG.error(
                'Unable to switch scene in OBS {}'.format(
                    getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()

    @check_connection
    async def show_source(self, source_name: str) -> None:
        """Show a source.

        Args:
            source_name (str): Name of the source to show.
        """
        scene = self.obs_connection.call(obs_requests.GetCurrentScene())
        if source_name not in scene.get_sources():
            LOG.error(
                f'Source: {source_name} does not exist in the current scene: '
                '{}.'.format(scene.getName())
            )
            return

        LOG.debug(f'Making source {source_name} visible')
        try:
            self.obs_connection.call(
                obs_requests.SetSceneItemProperties('Audio', visible=True)
            )

        except Exception as e:
            LOG.error(
                'Unable to show source in OBS {}'.format(
                    getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()

    @check_connection
    async def hide_source(self, source_name: str) -> None:
        """Hide a source.

        Args:
            source_name (str): Name of the source to hide.
        """
        scene = self.obs_connection.call(obs_requests.GetCurrentScene())
        if source_name not in scene.get_sources():
            LOG.error(
                f'Source: {source_name} does not exist in the current scene: '
                '{}.'.format(scene.getName())
            )
            return

        LOG.debug(f'Making source {source_name} hidden')
        try:
            self.obs_connection.call(
                obs_requests.SetSceneItemProperties('Audio', visible=False)
            )

        except Exception as e:
            LOG.error(
                'Unable to hide source in OBS {}'.format(
                    getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()

    async def on_event(self, message: object) -> None:
        """Runs when OBS sends any event.

        Used for debugging.

        Args:
            message (object): Event from OBS.
        """
        # LOG.debug(f'Got message: {message}')
        pass

    async def disconnect(self) -> None:
        """Disconnect from OBS."""
        if self.obs_connection.connected:
            self.obs_connection.disconnect()
