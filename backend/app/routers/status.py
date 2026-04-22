"""
Service status route handlers
"""

from fastapi import APIRouter, Depends
from httpx import AsyncClient
from app.dependencies.jwt_token import validate_token, AccessToken
from app.dependencies.http_client import get_http_client
from app.models.status import StatusResponse
from app.services import status

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
async def service_status(
    token: AccessToken = Depends(validate_token),
    client: AsyncClient = Depends(get_http_client),
) -> StatusResponse:
    """
    Authenticated endpoint returning health status of external services.

    Services are loaded from config. Results are cached to avoid excessive
    health checks. Requires a valid access token.

    Args:
        token (AccessToken): The access token used for authentication.
        client: The HTTP client used for making requests.

    Returns:
        StatusResponse with overall and per-service status.
    """
    return await status.fetch_service_status(client)
