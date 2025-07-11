"""
HTTP client dependency to make async http requests
"""

from typing import AsyncGenerator, Mapping, Any, Tuple
from httpx import AsyncClient, Response


# pylint: disable=too-many-arguments,too-many-positional-arguments
async def http_request(
    client: AsyncClient,
    method: str,
    url: str,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
    data: Mapping[str, Any] | None = None,
    json: Mapping[str, Any] | None = None,
    valid_status_codes: Tuple[int, ...] | None = None,
) -> Response:
    """
    Send an HTTP request and return the response.

    This function sends an HTTP request using the provided client and parameters,
    and returns the response. If the response status code is not in the list of
    valid status codes, it raises an exception.

    Args:
        client (AsyncClient): The HTTP client to use for the request.
        method (str): The HTTP method to use (e.g., 'GET', 'POST', etc.).
        url (str): The URL to send the request to.
        headers (Mapping[str, str], optional): The headers to include in the request.
        params (Mapping[str, Any], optional): The query parameters to include in the request.
        data (Mapping[str, Any], optional): The data to include in the request body.
            This data will be form-encoded before being sent.
        json (Mapping[str, Any], optional): The JSON serializable
            payload to include in the request body.
        valid_status_codes (Tuple[int, ...], optional):
            The status codes that indicate a successful request.

    Returns:
        Response: The HTTP response.

    Raises:
        RequestError: If there is an error sending the request
                      or if the response status code is not valid.
    """
    response: Response = await client.request(
        method=method, url=url, headers=headers, params=params, json=json, data=data
    )

    if valid_status_codes is None or response.status_code not in valid_status_codes:
        response.raise_for_status()

    return response
