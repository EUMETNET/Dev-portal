"""
Users route handlers
"""

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient
from app.config import settings, logger
from app.dependencies.jwt_token import validate_admin_role, AccessToken
from app.dependencies.http_client import get_http_client
from app.services import users
from app.models.responses import DeleteAPIKey
from app.exceptions import APISIXError, VaultError, KeycloakError

router = APIRouter()

config = settings()


@router.delete("/users/{user_uuid}", response_model=DeleteAPIKey)
async def delete_user(
    user_uuid: str,
    token: AccessToken = Depends(validate_admin_role),
    client: AsyncClient = Depends(get_http_client),
) -> DeleteAPIKey:
    """
    Delete a user from Keycloak and user's API key from Vault and APISIX(es).

    Args:
        user_uuid (str): The UUID of the user whose API key is to be deleted.
        token (AccessToken): The access token of the user to be deleted.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        JSONResponse: A response indicating whether the deletion was successful.

    Raises:
        HTTPException: If there is an error getting user info from APISIX or Vault,
                       or if there is an error deleting the user from Vault or APISIX.
    """
    admin_uuid = token.sub

    logger.info("Admin '%s' requested deletion of user '%s'", admin_uuid, user_uuid)

    try:
        await users.delete_or_disable_user(client, user_uuid, "DELETE")

    except (VaultError, APISIXError, KeycloakError) as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e)) from e

    return DeleteAPIKey()


@router.delete("/users/{user_uuid}/apikey", response_model=DeleteAPIKey)
async def delete_user_apikey(
    user_uuid: str,
    token: AccessToken = Depends(validate_admin_role),
    client: AsyncClient = Depends(get_http_client),
) -> DeleteAPIKey:
    """
    Delete a user's API key from Vault and APISIX(es) also disables user in Keycloak.

    Args:
        user_uuid (str): The UUID of the user whose API key is to be deleted.
        token (AccessToken): The access token of the user whose API key is to be deleted.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        JSONResponse: A response indicating whether the deletion was successful.

    Raises:
        HTTPException: If there is an error getting user info from APISIX or Vault,
                       or if there is an error deleting the user from Vault or APISIX.
    """
    admin_uuid = token.sub

    logger.info("Admin '%s' requested deletion of API key for user '%s'", admin_uuid, user_uuid)

    try:
        await users.delete_or_disable_user(client, user_uuid, "DISABLE")

    except (VaultError, APISIXError, KeycloakError) as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e)) from e

    return DeleteAPIKey()
