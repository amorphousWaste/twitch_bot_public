"""Template plugin to be used as an example.

This plugin will automatically be excluded.
"""

# This import allows you to create database fields.
from tortoise import fields

from plugins._base_model import AbstractPluginModel
from plugins._base_plugins import BaseCommandPlugin

# The CACHE is available for random data storage.
from init import CACHE


class TemplateCommandModel(AbstractPluginModel):
    """Template command model for the database.

    Ensure you change the name to match the plugin class itself.
    """

    # Define any custom database fields needed for this plugin here.
    # For information on how to add new database fields see the documentation
    # here: https://tortoise.github.io/fields.html

    class Meta:
        # This defines the name of the table to use for the plugin.
        # Change this to the name of the plugin class.
        table = 'TemplateCommandPlugin'


# Make sure you use the correct subclass for the type of plugin you are
# writing.
class TemplateCommandPlugin(BaseCommandPlugin):
    """Template plugin class.

    Plugins should be subclased from one of the plugin categories in
    base_plugins, but can use multiple inheritence if necessary.
    """

    # This is the string that will be used to run this plugin.
    COMMAND = 'command'

    # --- Optional Attributes --- #

    # This sets permissions for the plugin. If not included, anyone can run it.
    # The owner is automatically allowed to run everything.
    # Accepted values are 'bot', 'mod' and/or 'regular'.
    # Using 'bot' excludes everyone else since bot is assumed.
    ALLOWED = ['bot', 'mod', 'regular']

    # This will block the plugin from running for the given amount of minutes.
    # If not provided, there will be no timeout.
    TIMEOUT = 0

    # This will block a user from running the command for a given amount of
    # minutes. The command can be run immediately by another user.
    # If not provided, there will be no timeout.
    USER_TIMEOUT = 0

    # This will add a new row in the database setting the given fields to
    # the given values. If not provided, no action is taken.
    RESET = {'field1': 'value1', 'field2': 'value2'}

    async def run(self):
        """Run function"""
        # Your code goes here.
