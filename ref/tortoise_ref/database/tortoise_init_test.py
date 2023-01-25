#!/usr/bin/env python
"""Test of initializing a database via Tortoise ORM."""

import logging
import os

from tortoise import Tortoise

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s %(asctime)s [%(filename)s:%(lineno)d]> %(message)s',
    datefmt='%Y/%m/%d %I:%M:%S%p',
)
LOG = logging.getLogger('tortoise_test')


async def init_db():
    """Run the database initialization."""
    db_path = os.path.join(os.path.dirname(__file__), 'twitch_bot.db')

    models = ['database.tortoise_model_test']
    for plugin_file in os.listdir(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
    ):
        if plugin_file.startswith('_templates'):
            continue

        models.append('plugins.{}'.format(os.path.splitext(plugin_file)[0]))
    LOG.debug(models)

    # Initialize the database connection and auto-discover the models.
    await Tortoise.init(
        db_url=f'sqlite:///{db_path}',
        modules={'models': models},
    )
    # Generate the schema.
    await Tortoise.generate_schemas()


async def close_db():
    """Close the database."""
    await Tortoise.close_connections()
