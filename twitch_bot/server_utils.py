"""Requests stuff."""

import aiohttp
import traceback

from typing import Callable, Optional

from log import LOG


class DummyResponse(object):
    """DummyResponse object used to return data when bad requests are made.

    This allows us to return something valid without checking every time.
    """

    def __init__(self) -> None:
        """Init."""
        super(DummyResponse, self).__init__()

    async def json(self) -> dict:
        """Mock the return data as a dictionary.

        Returns:
            (dict): Empty dictionary.
        """
        return {}


def check_server_response(func: Callable) -> Callable:
    """Decorator to check the response from the server."""

    async def wrapper(*args, **kwargs) -> aiohttp.ClientResponse:
        """Check server response code."""
        # Ensure the response from the server did not error out.
        try:
            response, data = await func(*args, **kwargs)

        except Exception as e:
            LOG.error(
                'Unable to communicate properly with server: {}'.format(
                    getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()

            return {}

        # Check the response from the server.
        # Anything in the 2XX range is considered OK.
        # Anything else is considered an error.
        response_code = response.status
        if response_code < 200 or response_code > 299:
            LOG.error(
                f'Request to {response.url} returned error {response_code}: '
                f'{response.reason}'
            )

        return response_code, data

    return wrapper


@check_server_response
async def get_request(
    url: str, headers: dict, params: Optional[dict] = {}
) -> aiohttp.ClientResponse:
    """Send a get request and return the response.

    Args:
        url (str): The URL to make the request to.
        headers (dict): Request headers.
        params (dict, optional): Request parameters.

    Returns:
        response (response): Response from the server.
        data: (dict): JSON data from the response.
    """
    LOG.debug(f'GET: {url} {headers} {params}')
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params) as response:
            try:
                data = await response.json()

            except aiohttp.client_exceptions.ContentTypeError:
                LOG.warning(
                    'Could not decode JSON object. '
                    'If the response is OK, there probably was none.'
                )
                data = {}

            return response, data


@check_server_response
async def post_request(
    url: str,
    data: dict,
    headers: Optional[dict] = {},
    params: Optional[dict] = {},
) -> aiohttp.ClientResponse:
    """Send a POST request and return the response.

    Args:
        url (str): The URL to make the request to.
        data (dict): Request data.
        headers (dict, optional): Request headers.
        params (dict, optional): Request parameters.

    Returns:
        response (response): Response from the server.
        data: (dict): JSON data from the response.
    """
    LOG.debug(f'POST: {url} {headers} {data} {params}')
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, headers=headers, data=data, params=params
        ) as response:
            try:
                data = await response.json()

            except aiohttp.client_exceptions.ContentTypeError:
                LOG.warning(
                    'Could not decode JSON object. '
                    'If the response is OK, there probably was none.'
                )
                data = {}

            return response, data


@check_server_response
async def delete_request(
    url: str, headers: dict, params: Optional[dict] = {}
) -> aiohttp.ClientResponse:
    """Send a DELETE request and return the response.

    Args:
        url (str): The URL to make the request to.
        headers (dict): Request headers.
        params (dict, optional): Request parameters.

    Returns:
        response (response): Response from the server.
        data: (dict): JSON data from the response.
    """
    LOG.debug(f'DELETE: {url} {headers} {params}')
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.delete(url, params=params) as response:
            try:
                data = await response.json()

            except aiohttp.client_exceptions.ContentTypeError:
                LOG.warning(
                    'Could not decode JSON object. '
                    'If the response is OK, there probably was none.'
                )
                data = {}

            return response, data


@check_server_response
async def patch_request(
    url: str, headers: dict, params: dict, patch: dict
) -> aiohttp.ClientResponse:
    """Send a PATCH request and return the response.

    Args:
        url (str): The URL to make the request to.
        headers (dict): Request headers.
        params (dict): Request parameters.
        patch (dict): Patch data.

    Returns:
        response (response): Response from the server.
        data: (dict): JSON data from the response.
    """
    LOG.debug(f'PATCH: {url} {headers} {params} {patch}')
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.patch(url, data=patch, params=params) as response:
            LOG.debug(f'response: {response}')
            try:
                data = await response.json()

            except aiohttp.client_exceptions.ContentTypeError:
                LOG.warning(
                    'Could not decode JSON object. '
                    'If the response is OK, there probably was none.'
                )
                data = {}

            return response, data
