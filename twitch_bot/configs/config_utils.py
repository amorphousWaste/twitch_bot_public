"""Config Utils."""

import aiofiles
import os
import traceback
import yaml

from init import CACHE
from log import LOG


async def load_cached_config(config_name: str) -> dict:
    """Load a config from the cache if it exists.

    Args:
        config_name (str): Config name.

    Returns:
        (dict): Config data if it exists.
    """
    config_cache = await CACHE.get('configs')

    if not config_cache:
        LOG.debug('Creating config cache.')
        # Assume the config is good for 6 hours.
        config_cache = await CACHE.add('configs', data={}, duration=360)

    return config_cache.data.get(config_name, {})


async def cache_config(config_name: str, config_data: dict) -> None:
    """Cache or update the cache for a config.

    Args:
        config_name (str): Config name.
        config_data (dict): Config description.
    """
    config_cache = await CACHE.get('configs')
    config_cache.data[config_name] = config_data


async def load_config_file(config_name: str, refresh: bool = False) -> str:
    """Load a config file.

    Args:
        config_name (str): Name of the config file.
        refresh (bool): Force the reloading of the config.

    Returns:
        (dict): Contents of the config as a dictionary.
    """
    if not refresh:
        # If the config is cached, return the cached config.
        config_data = await load_cached_config(config_name)
        if config_data:
            LOG.debug(f'Loaded cached config {config_name}: {config_data}')
            return config_data

    # Build a path from the config name.
    config_path = os.path.join(
        os.path.dirname(__file__), f'{config_name}.yaml'
    )

    if not os.path.exists(config_path):
        LOG.error(f'Config does not exist: {config_path}')
        return {}

    try:
        async with aiofiles.open(config_path, 'r', encoding='utf8') as in_file:
            raw_config_data = await in_file.read()

        config_data = yaml.safe_load(raw_config_data)

        # Cache the config data.
        await cache_config(config_name, config_data)

    except Exception as e:
        LOG.error(
            'Unable to load config file {}: {}'.format(
                config_path, getattr(e, 'message', repr(e))
            )
        )
        # If the level is 'debug', print the traceback as well.
        if LOG.level == 0:
            traceback.print_exc()

        return {}

    LOG.debug(f'Loaded written config {config_name}: {config_data}')
    return config_data


async def write_config_file(config_name: str, config_data: dict) -> None:
    """Write or overwrite a config file.

    Args:
        config_name (str): Name of the config file.
        config_data (dict): Data to write.
    """
    # Build a path from the config name.
    config_path = os.path.join(
        os.path.dirname(__file__), f'{config_name}.yaml'
    )

    try:
        # 2021/10/20: It appears at this point writing to YAML cannot be
        # async.
        with open(config_path, 'w') as out_file:
            yaml.dump(config_data, out_file)

    except Exception as e:
        LOG.error(
            'Unable to write config file {}: {}'.format(
                config_path, getattr(e, 'message', repr(e))
            )
        )
        # If the level is 'debug', print the traceback as well.
        if LOG.level == 0:
            traceback.print_exc()

    # Cache the config data.
    await cache_config(config_name, config_data)


async def write_config_values(config_name: str, config_data: dict) -> None:
    """Write the data to a config file.

    This loads the config first, replaces the values and write it out.

    Args:
        config_name (str): Name of the config file.
        config_data (dict): Data to write.
    """
    # Load the existing config.
    original_config_data = await load_config_file(config_name)

    # Update the config dictionary.
    updated_data = original_config_data | config_data
    await write_config_file(config_name, updated_data)
