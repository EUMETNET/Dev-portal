"""
API key route handlers
"""

from http import HTTPStatus
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient, HTTPError
from app.config import settings, logger
from app.dependencies.jwt_token import validate_token, AccessToken
from app.dependencies.http_client import get_http_client
from app.services import vault, apisix
from app.utils.uuid import remove_dashes
from app.models.apisix import APISixConsumer
from app.models.vault import VaultUser
from app.models.responses import GetAPIKey, DeleteAPIKey

router = APIRouter()

config = settings()


async def get_user_from_vault_and_apisixes(
    client: AsyncClient, uuid_not_dashes: str
) -> tuple[VaultUser | None, list[APISixConsumer | None]]:
    """
    Get user info from Vault and APISix instances.

    Args:
        client (AsyncClient): The HTTP client to use for making requests.
        uuid_not_dashes (str): The user's UUID without dashes.

    Returns:
        tuple[vault.VaultUser | None, list[str]]:
            The user's information from Vault and the APISix instances where the user exists.
    """
    try:
        results = await asyncio.gather(
            vault.get_user_info_from_vault(client, uuid_not_dashes),
            *apisix.create_tasks(apisix.get_apisix_consumer, client, uuid_not_dashes),
        )
        return results[0], results[1:]
    except HTTPError as e:
        logger.exception(
            "Error getting user '%s' from APISix or Vault.", uuid_not_dashes, exc_info=e
        )
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="APISix and or Vault service error"
        ) from e


# For now just refactor the existing endpoint as is
# Either naming this route differently or creating routes for routes and apikey
@router.get("/getapikey", response_model=GetAPIKey)
async def get_api_key(
    token: AccessToken = Depends(validate_token),
    client: AsyncClient = Depends(get_http_client),
) -> GetAPIKey:
    """
    Retrieve the API key for a user.

    This function retrieves the user's API key from Vault and APISix.
    If the user does not exist in Vault, it saves the user to Vault.
    If the user does not exist in APISix, it creates the user in APISix.

    Args:
        token (AccessToken): The access token of the user.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        JSONResponse: A response containing the user's API key
                      and the routes that require key authentication.

    Raises:
        HTTPException: If there is an error getting user info from APISix or Vault,
                       or if there is an error saving the user to Vault or APISix.
    """
    uuid = token.sub
    uuid_not_dashes = remove_dashes(uuid)

    logger.debug("Got request to retrieve API key for user '%s'", uuid_not_dashes)

    vault_user, apisix_users = await get_user_from_vault_and_apisixes(client, uuid_not_dashes)

    apisix_instances_with_no_user = apisix.apisix_instances_missing_user(apisix_users)

    if not vault_user:
        logger.debug("User '%s' not found in Vault --> Saving user to Vault", uuid_not_dashes)
        try:
            vault_user = await vault.save_user_to_vault(client, uuid_not_dashes)
        except HTTPError as e:
            logger.exception("Error saving user '%s' to Vault", uuid_not_dashes, exc_info=e)
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="Vault service error"
            ) from e

    if apisix_instances_with_no_user:
        logger.debug(
            "User '%s' not found in following APISix instances: %s -->"
            "Creating user to these instances",
            uuid_not_dashes,
            ",".join(apisix_instances_with_no_user),
        )
        try:
            await asyncio.gather(
                *apisix.create_tasks(
                    apisix.create_apisix_consumer,
                    client,
                    uuid_not_dashes,
                    instances=apisix_instances_with_no_user,
                )
            )
        except HTTPError as e:
            logger.exception(
                "Error saving user '%s' to APISIX instances: %s",
                uuid_not_dashes,
                apisix_instances_with_no_user,
                exc_info=e,
            )
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail="APISix service error",
            ) from e

    api_key = vault_user.auth_key

    logger.debug("retrieving all the routes that requires key authentication")
    routes_responses = await asyncio.gather(*apisix.create_tasks(apisix.get_routes, client))

    routes = [route for response in routes_responses for route in response.routes]
    logger.debug("found %s routes: %s", len(routes), routes)

    return GetAPIKey(apiKey=api_key, routes=routes)


@router.delete("/apikey", response_model=DeleteAPIKey)
async def delete_user(
    token: AccessToken = Depends(validate_token),
    client: AsyncClient = Depends(get_http_client),
) -> DeleteAPIKey:
    """
    Delete a user from both Vault and APISix.

    This function first retrieves the user's information from both Vault and APISix.
    If the user exists in Vault, it deletes the user from Vault.
    If the user exists in APISix, it deletes the user from APISix.

    Args:
        token (AccessToken): The access token of the user to be deleted.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        JSONResponse: A response indicating whether the deletion was successful.

    Raises:
        HTTPException: If there is an error getting user info from APISix or Vault,
                       or if there is an error deleting the user from Vault or APISix.
    """
    uuid = token.sub
    uuid_not_dashes = remove_dashes(uuid)

    logger.debug("Got request to retrieve API key for user '%s'", uuid_not_dashes)

    vault_user, apisix_users = await get_user_from_vault_and_apisixes(client, uuid_not_dashes)

    apisix_instances_with_user = set(user.instance_name for user in apisix_users if user)

    if vault_user:
        logger.debug("User '%s' found from Vault --> Deleting user from Vault", uuid_not_dashes)
        try:
            await vault.delete_user_from_vault(client, uuid_not_dashes)
        except HTTPException as e:
            logger.exception("Error deleting user from Vault: %s", e)
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="Vault service error"
            ) from e

    if apisix_instances_with_user:
        logger.debug(
            "User '%s' found in following APISix instances: %s --> Deleting user from those",
            uuid_not_dashes,
            ",".join(apisix_instances_with_user),
        )
        try:
            await asyncio.gather(
                *apisix.create_tasks(
                    apisix.delete_apisix_consumer,
                    client,
                    uuid_not_dashes,
                    instances=apisix_instances_with_user,
                )
            )
        except HTTPException as e:
            logger.exception(
                "Error deleting user '%s' from APISix instances: %s",
                uuid_not_dashes,
                apisix_instances_with_user,
                exc_info=e,
            )
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail="APISix service error",
            ) from e

    return DeleteAPIKey()
