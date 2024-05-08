"""
API key route handlers
"""

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient
from app.config import settings, logger
from app.dependencies.jwt_token import validate_token, AccessToken
from app.dependencies.http_client import get_http_client
from app.services import apikey
from app.utils.uuid import remove_dashes
from app.models.responses import GetAPIKey, MessageResponse
from app.exceptions import APISIXError, VaultError

router = APIRouter()

config = settings()


# For now just refactor the existing endpoint as is
# Either naming this route differently or creating routes for routes and apikey
@router.get("/apikey", response_model=GetAPIKey)
async def get_api_key(
    token: AccessToken = Depends(validate_token),
    client: AsyncClient = Depends(get_http_client),
) -> GetAPIKey:
    """
    Retrieve the API key for a user.

    This function retrieves the user's API key from Vault and APISIX.
    If the user does not exist in Vault, it saves the user to Vault.
    If the user does not exist in APISIX, it creates the user in APISIX.

    Args:
        token (AccessToken): The access token of the user.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        GetAPIKey: A response containing the user's API key.

    Raises:
        HTTPException: If there is an error getting user info from APISIX or Vault,
                       or if there is an error saving the user to Vault or APISIX.
    """
    uuid = token.sub
    uuid_no_dashes = remove_dashes(uuid)

    logger.debug("Got request to retrieve API key for user '%s'", uuid_no_dashes)

    try:
        vault_user, apisix_users = await apikey.get_user_from_vault_and_apisixes(
            client, uuid_no_dashes
        )

        if not vault_user or any(user is None for user in apisix_users):
            logger.debug("User '%s' not found in Vault or APISIX --> Creating user", uuid_no_dashes)
            vault_user = await apikey.create_user_to_vault_and_apisixes(
                client, uuid_no_dashes, vault_user, apisix_users
            )

    except (VaultError, APISIXError) as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e)) from e

    api_key = vault_user.auth_key

    return GetAPIKey(apiKey=api_key)


@router.delete("/apikey", response_model=MessageResponse)
async def delete_user(
    token: AccessToken = Depends(validate_token),
    client: AsyncClient = Depends(get_http_client),
) -> MessageResponse:
    """
    Delete a user from both Vault and APISIX.

    This function first retrieves the user's information from both Vault and APISIX.
    If the user exists in Vault, it deletes the user from Vault.
    If the user exists in APISIX, it deletes the user from APISIX.

    Args:
        token (AccessToken): The access token of the user to be deleted.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        MessageResponse: A response indicating whether the deletion was successful.

    Raises:
        HTTPException: If there is an error getting user info from APISIX or Vault,
                       or if there is an error deleting the user from Vault or APISIX.
    """
    uuid = token.sub
    uuid_no_dashes = remove_dashes(uuid)

    logger.debug("Got request to delete API key for user '%s'", uuid_no_dashes)

    try:
        vault_user, apisix_users = await apikey.get_user_from_vault_and_apisixes(
            client, uuid_no_dashes
        )
        if vault_user or any(apisix_users):
            logger.debug("User '%s' found in Vault and/or APISIX --> Deleting user", uuid_no_dashes)
            await apikey.delete_user_from_vault_and_apisixes(
                client, uuid_no_dashes, vault_user, apisix_users
            )

    except (VaultError, APISIXError) as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e)) from e

    return MessageResponse(message="OK")
