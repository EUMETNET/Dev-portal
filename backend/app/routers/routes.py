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
from app.models.response import GetRoutes, RouteWithLimits
from app.models.apisix import APISixConsumer
from app.models.request import User

router = APIRouter()

config = settings()


# For now just refactor the existing endpoint as is
# Either naming this route differently or creating routes for routes and apikey
@router.get("/routes", response_model=GetRoutes)
async def get_routes(
    token: AccessToken = Depends(validate_token),
    client: AsyncClient = Depends(get_http_client),
) -> GetRoutes:
    """
    Retrieve all the APISIX routes that requires key authentication.

    Args:
    - token (AccessToken): The access token used for authentication.
    - client (AsyncClient): The HTTP client used for making requests.

    Returns:
    - GetRoutes: An object containing the retrieved routes with rate limits.

    Raises:
    - HTTPException: If there is an error retrieving the routes.

    """

    logger.debug("Got a request to retrieve all the APISIX routes")

    logger.debug("retrieving all the routes that requires key authentication")

    # Get APISIX consumer for the user from all instances
    user = User(id=token.sub, groups=token.groups)
    apisix_consumers = await asyncio.gather(
        *apisix.create_tasks(apisix.get_apisix_consumer, client, user.id),
        return_exceptions=True,
    )
    valid_consumers = [
        consumer if isinstance(consumer, APISixConsumer) else None for consumer in apisix_consumers
    ]

    routes_responses = await asyncio.gather(
        *[
            apisix.get_routes_with_limits(client, instance, consumer)
            for instance, consumer in zip(config.apisix.instances, valid_consumers)
        ],
        return_exceptions=True,
    )

    # Routes are same across all instances so error only if all instances failed
    if all(isinstance(response, Exception) for response in routes_responses):
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail=str(routes_responses[0]),
        )

    all_routes = []
    for response in routes_responses:
        if isinstance(response, list):
            all_routes.extend(response)

    unique_routes_dict = {}
    for route in all_routes:
        url = route["url"]
        if url not in unique_routes_dict:
            unique_routes_dict[url] = route

    routes_with_limits = [
        RouteWithLimits(
            url=route["url"],
            limits=route["limits"],
        )
        for route in unique_routes_dict.values()
    ]

    logger.debug("found %s unique routes: %s", len(routes_with_limits), routes_with_limits)
    return GetRoutes(routes=routes_with_limits)
