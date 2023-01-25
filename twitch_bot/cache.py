"""Data Cache.

Transient arbitrary data storage.
"""

import asyncio
import datetime
import re
import traceback

from typing import Optional


class CacheData(object):
    """Object for storing data in the cache."""

    def __init__(self, data: object, duration: Optional[int] = None) -> None:
        """Init.

        Args:
            data (object): Value to store.
            duration (int, optional): Length of time in minutes to store the
                data.
                Default is no duration.
        """
        super(CacheData, self).__init__()

        self.data = data
        self.creation_time = datetime.datetime.now()

        if duration:
            self.duration = datetime.timedelta(minutes=duration)
            self.expiration = self.creation_time + self.duration

        else:
            self.duration = None
            self.expiration = None

    @property
    async def expired(self) -> bool:
        """True if expired, otherwise False."""
        if not self.expiration:
            return False

        return datetime.datetime.now() > self.expiration

    @property
    async def remaining(self) -> int:
        """Return time remaining before the data expires.

        If there is no experation, returns -1.
        """
        if not self.expiration:
            return -1

        if self.expired():
            return 0

        remaining = datetime.datetime.now() - self.expiration
        return int(remaining.total_seconds / 60)


class Cache(object):
    """In-memory data cache."""

    def __init__(self) -> None:
        """Init."""
        super(Cache, self).__init__()

        self.cache = {}

    async def add(
        self,
        key: str,
        data: Optional[object] = None,
        duration: Optional[int] = None,
        overwrite: Optional[bool] = True,
    ) -> bool:
        """Add data into the cache.

        Args:
            key (str): Key to store the data with.
            data (object, optional): Data to store.
            duration (int, optional): Length of time in minutes to store the
                data. Default is no duration.
            overwrite (bool, optional): Whether or not to overwrite the data
                if it exists. Default is True.

        Returns:
            (CacheData|None): CacheData if the data was added correctly,
                otherwise None.
        """
        if key in self.cache and not self.cache[key].expired and not overwrite:
            return None

        try:
            self.cache[key] = CacheData(data, duration)

        except Exception:
            traceback.print_exc()
            return None

        return self.cache[key]

    async def get(self, key: str) -> CacheData:
        """Get data from the cache if it exists.

        Args:
            key (str): Key to store the data with.

        Returns:
            (CacheData | None): The matching data if it exists, otherwise None.
        """
        return self.cache.get(key, None)

    async def exists(self, key: str) -> bool:
        """Check if the key exists in the cache.

        Args:
            key (str): Key to store the data with.

        Returns:
            (bool): True if the key exists in the cache, otherwise False.
        """
        return True if key in self.cache else False

    async def find(self, search: str) -> CacheData:
        """Find a key from a search string.

        Supports regex.

        Args:
            search (str): Search string.

        Returns:
            (list): List of CacheData where the key matches the search string.
        """
        found = []
        for key in await self.list():
            match = re.search(search, key)
            if not match:
                continue

            found.append(await self.get(key))

        return found

    async def list(self) -> list:
        """Return a list of keys in the cache."""
        return list(self.cache.keys())

    async def extend(self, key: str, length: Optional[int] = 60) -> None:
        """Extend the given keys duration.

        Args:
            key (str): Key to renew.
            length (int, optional): Length of time in minutes to store the
                data.
                Default is no duration.
        """
        if await self.exists(key) and self.cache[key].expiration:
            extension = datetime.timedelta(minutes=length)
            self.cache[key].duration += extension
            self.cache[key].expiration += extension

    async def delete(self, key: str) -> None:
        """Delete the key and associated data if it exists.

        Args:
            key (str): Key to delete.

        Returns:
            (bool): True if the key exists in the cache, otherwise False.
        """
        if key not in self.cache:
            return False

        try:
            del self.cache[key]

        except Exception:
            traceback.print_exc()
            return False

        return True

    async def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()

    async def clean(self) -> None:
        """Clean expired keys from the cache."""
        for key in list(self.cache.keys()):
            if await self.cache[key].expired:
                await self.delete(key)

    async def clean_task(self) -> None:
        """Asynchronous task for cleaning the cache of expired keys."""
        while True:
            await asyncio.sleep(60)
            await self.clean()
