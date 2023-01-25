"""Quickly initialize the bot for testing.

Meant to be copied and pasted into iPython.
"""

from auth import Auth
from bot import TwitchBot
from chat.chat_connection import ChatConnection

authorization = await Auth().init()
connection = await ChatConnection().init(authorization)
bot = await TwitchBot().init(authorization, connection)
