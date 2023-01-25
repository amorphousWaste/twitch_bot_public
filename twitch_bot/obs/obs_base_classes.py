"""Base classes."""

import copy


class BaseEvents(object):
    """Base class for events."""

    def __init__(self):
        """Init."""
        super(BaseEvents, self).__init__()

        self.name = None
        self.data_in = {}

    async def init(self) -> object:
        """Async init.

        Returns:
            self (self): Class instance.
        """
        return self

    async def input(self, data: dict) -> None:
        """Data input.

        Args:
            data (dict): Event data.
        """
        self.data_in = data


class BaseRequests(object):
    """Base class for requests."""

    def __init__(self):
        """Init."""
        super(BaseRequests, self).__init__()

        self.name = None
        self.data_in = {}
        self.data_out = {}
        self.status = None

    async def init(self) -> object:
        """Async init.

        Returns:
            self (self): Class instance.
        """
        return self

    async def data(self) -> dict:
        """Data payload from the request.

        Returns:
            payload (dict): Payload from OBS.
        """
        payload = copy.copy(self.data_out)
        payload.update({'request-type': self.name})

        return payload

    async def input(self, data: dict) -> None:
        """Data input.

        Args:
            data (dict): Event data.
        """
        self.status = data['status'] == 'ok'
        self.data_in = data
