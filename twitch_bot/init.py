"""Initialization Setup."""

import asyncio
import sys

from cache import Cache
from exceptions import excepthook

CACHE = Cache()

EVENT_QUEUE = asyncio.Queue()

# Set the global excepthook for unhandled errors.
sys.excepthook = excepthook.handler
