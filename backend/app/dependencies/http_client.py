"""
HTTP client dependency to make (a)sync http requests
"""

from typing import AsyncGenerator
from httpx import AsyncClient

async def get_http_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Asynchronous generator function that yields an instance of httpx.AsyncClient.

    This function is used as a dependency in FastAPI route handlers to provide an HTTP client for making requests.

    Yields:
    AsyncClient: An instance of httpx.AsyncClient. The client is automatically closed when the request is finished.
    """
    async with AsyncClient() as client:
        yield client