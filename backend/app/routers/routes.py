"""
'Route' routes handlers
"""

from http import HTTPStatus
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient
from app.config import settings, logger
from app.dependencies.jwt_token import validate_token, AccessToken
from app.dependencies.http_client import get_http_client
from app.services import apisix
from app.models.response import GetRoutes
from app.models.apisix import APISixRoutes
from app.exceptions import APISIXError

router = APIRouter()

config = settings()


# For now just refactor the existing endpoint as is
# Either naming this route differently or creating routes for routes and apikey
@router.get("/routes", response_model=GetRoutes)
async def get_routes(
    _token: AccessToken = Depends(validate_token),
    client: AsyncClient = Depends(get_http_client),
) -> GetRoutes:
    """
    Retrieve all the APISIX routes that requires key authentication.

    Args:
    - _token (AccessToken): The access token used for authentication.
    - client (AsyncClient): The HTTP client used for making requests.

    Returns:
    - GetRoutes: An object containing the retrieved routes.

    Raises:
    - HTTPException: If there is an error retrieving the routes.

    """

    logger.debug("Got a request to retrieve all the APISIX routes")

    logger.debug("retrieving all the routes that requires key authentication")

    routes_responses: list[APISixRoutes | APISIXError] = await asyncio.gather(
        *apisix.create_tasks(apisix.get_routes, client), return_exceptions=True
    )

    # Routes are same across all instances so error only if all instances failed
    if all(isinstance(response, APISIXError) for response in routes_responses):
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail=str(routes_responses[0]),
        )

    routes = [
        route
        for response in routes_responses
        if isinstance(response, APISixRoutes)
        for route in response.routes
    ]
    unique_routes = list(set(routes))
    logger.debug("found %s unique routes: %s", len(unique_routes), unique_routes)

    return GetRoutes(routes=unique_routes)
