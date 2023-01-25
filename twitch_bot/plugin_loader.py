"""Plugin Manager."""

import importlib
import inspect
import os

from configs import config_utils
from plugins import _base_plugins


async def import_plugins(do_reload: bool = False) -> dict:
    """Import the plugins from the plugin files.

    Args:
        reload (bool): Used to signal that the plugins should be reloaded.

    Returns:
        imported_plugins (dict): Imported plugins.
    """
    # Find all the files in the plugins folder that don't start with '_'.
    plugin_files = [
        os.path.splitext(p)[0]
        for p in os.listdir('plugins')
        if not p.startswith('_')
    ]

    # Import all the plugins.
    imported_plugins = [
        importlib.import_module(f'plugins.{plugin_file}', '.')
        for plugin_file in plugin_files
    ]

    if do_reload:
        imported_plugins = [importlib.reload(ip) for ip in imported_plugins]

    return imported_plugins


async def load_plugins(do_reload: bool = False) -> dict:  # noqa: mccabe
    """Load all the plugins.

    Args:
        reload (bool): Used to signal that the plugins should be reloaded.

    Returns:
        plugins (dict): Dictionary of plugins in the form
            {
                category1: [
                    {name1: plugin1},
                    {name2: plugin2},
                ],
                category2: [
                    {name3: plugin3},
                ],
            }
    """
    imported_plugins = await import_plugins(do_reload)

    config = await config_utils.load_config_file('bot_config')

    plugins = {}

    # Build a dictionary of plugins.
    for imported_plugin in imported_plugins:
        for member in inspect.getmembers(imported_plugin, inspect.isclass):
            name, plugin = member

            # Ignore the base plugins.
            if name in [
                'BaseCommandPlugin',
                'BaseIntervalPlugin',
                'BaseRedemptionPlugin',
            ]:
                continue

            # Do not load blacklisted plugins.
            if name in config.get('blocklist'):
                continue

            if issubclass(
                plugin,
                (
                    _base_plugins.BaseCommandPlugin,
                    _base_plugins.BaseIntervalPlugin,
                ),
            ):
                plugin_category = 'command'
                if not plugins.get(plugin_category):
                    plugins[plugin_category] = {}

                plugins[plugin_category][plugin.COMMAND] = plugin

            if issubclass(plugin, _base_plugins.BaseIntervalPlugin):
                plugin_category = 'interval'
                if not plugins.get(plugin_category):
                    plugins[plugin_category] = {}

                plugins[plugin_category][plugin.COMMAND] = plugin

            if issubclass(plugin, _base_plugins.BaseRedemptionPlugin):
                plugin_category = 'redemption'
                if not plugins.get(plugin_category):
                    plugins[plugin_category] = {}

                plugins[plugin_category][plugin.COMMAND] = plugin

    return plugins
