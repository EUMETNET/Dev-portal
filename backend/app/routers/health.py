"""
Health check endpoint
"""

from http import HTTPStatus
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient
from app.config import logger
from app.dependencies.http_client import get_http_client
from app.services import vault, apisix
from app.models.response import MessageResponse
from app.exceptions import APISIXError, VaultError

router = APIRouter()


# For now just refactor the existing endpoint as is
# Either naming this route differently or creating routes for routes and apikey
@router.get("/health", response_model=MessageResponse)
async def health_check(client: AsyncClient = Depends(get_http_client)) -> MessageResponse:
    """
    Endpoint for performing health check.
    It checks the health of Vault and APISIX instances.

    Args:
    - client (AsyncClient): The HTTP client used for making requests.

    Returns:
    - MessageResponse: The health status of the service.

    Raises:
    - HTTPException: If there is an error during the health check.

    """

    logger.debug("Got a request to perform health check")
    logger.debug("Checking the health of Vault and APISIX instances...")

    results = await asyncio.gather(
        *vault.create_tasks(vault.healthcheck, client),
        *apisix.create_tasks(apisix.get_routes, client),
        return_exceptions=True,
    )

    if any(isinstance(result, (APISIXError, VaultError)) for result in results):
        logger.error("Error(s) during health check")
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail="Vault and/or APISIX instances are not healthy",
        )

    logger.debug("Vault and APISIX instances are healthy")
    return MessageResponse(message="OK")
