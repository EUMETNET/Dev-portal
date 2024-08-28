"""
Users route handlers
"""

from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Body
from httpx import AsyncClient
from app.config import settings, logger
from app.dependencies.jwt_token import validate_admin_role, AccessToken
from app.dependencies.http_client import get_http_client
from app.models.request import UserGroup
from app.models.response import MessageResponse
from app.services import users
from app.services import keycloak
from app.exceptions import APISIXError, VaultError, KeycloakError

router = APIRouter()

config = settings()


@router.delete("/admin/users/{user_uuid}", response_model=MessageResponse)
async def delete_user(
    user_uuid: str,
    token: AccessToken = Depends(validate_admin_role),
    client: AsyncClient = Depends(get_http_client),
) -> MessageResponse:
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
        keycloak_user = await keycloak.get_user(client, user_uuid)

        if keycloak_user is None or not keycloak_user.id:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail=f"User {user_uuid} not found"
            )

        await users.delete_or_disable_user(client, user_uuid, keycloak_user, "DELETE")

    except (VaultError, APISIXError, KeycloakError) as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e)) from e

    return MessageResponse(message="OK")


@router.put("/admin/users/{user_uuid}/disable", response_model=MessageResponse)
async def disable_user(
    user_uuid: str,
    token: AccessToken = Depends(validate_admin_role),
    client: AsyncClient = Depends(get_http_client),
) -> MessageResponse:
    """
    Disables a user in Keycloak and deletes user's existing API key from Vault and APISIX(es).

    Args:
        user_uuid (str): The UUID of the user whose API key is to be deleted.
        token (AccessToken): The access token of the user whose API key is to be deleted.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        JSONResponse: A response indicating whether the operation was successful.

    Raises:
        HTTPException: If there is an error communicating with Keycloak, Vault or APISIX.
    """
    admin_uuid = token.sub

    logger.info("Admin '%s' requested disabling the user '%s'", admin_uuid, user_uuid)

    try:
        keycloak_user = await keycloak.get_user(client, user_uuid)

        if keycloak_user is None or not keycloak_user.id:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

        await users.delete_or_disable_user(client, user_uuid, keycloak_user, "DISABLE")

    except (VaultError, APISIXError, KeycloakError) as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e)) from e

    return MessageResponse(message="OK")


@router.put("/admin/users/{user_uuid}/enable", response_model=MessageResponse)
async def enable_user(
    user_uuid: str,
    token: AccessToken = Depends(validate_admin_role),
    client: AsyncClient = Depends(get_http_client),
) -> MessageResponse:
    """
    Enables a user in Keycloak.

    Args:
        user_uuid (str): The UUID of the user whose API key is to be deleted.
        token (AccessToken): The access token of the user whose API key is to be deleted.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        JSONResponse: A response indicating whether the operation was successful.

    Raises:
        HTTPException: If there is an error communicating with Keycloak.
    """
    admin_uuid = token.sub

    logger.info("Admin '%s' requested enabling the user '%s'", admin_uuid, user_uuid)

    try:
        keycloak_user = await keycloak.get_user(client, user_uuid)

        if keycloak_user is None or not keycloak_user.id:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail=f"User {user_uuid} not found"
            )

        keycloak_user.enabled = True
        await keycloak.update_user(client, user_uuid, keycloak_user)

    except (VaultError, APISIXError, KeycloakError) as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e)) from e

    return MessageResponse(message="OK")


@router.put("/admin/users/{user_uuid}/update-group", response_model=MessageResponse)
async def update_user_to_group(
    user_uuid: str,
    user_group: UserGroup = Body(...),
    token: AccessToken = Depends(validate_admin_role),
    client: AsyncClient = Depends(get_http_client),
) -> MessageResponse:
    """
    Add a user to the given group in Keycloak.
    If user has existing API key, it will be added to group accordingly.

    Args:
        user_uuid (str): The UUID of the user.
        user_group (UserGroup): The group to which the user will be added.
        token (AccessToken): The access token of the user making the request.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        JSONResponse: A response indicating whether the operation was successful.

    Raises:
        HTTPException: If there is an error communicating with Keycloak, Vault, or APISIX.
    """
    admin_uuid = token.sub

    logger.info(
        "Admin '%s' requested promoting user '%s' to '%s' group",
        admin_uuid,
        user_uuid,
        user_group.group_name,
    )

    try:
        groups = await keycloak.get_groups(client)

        if (
            group_to_update := next((group for group in groups if group.name == user_group.group_name), None)
        ) is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Group '{user_group.group_name}' not found",
            )

        keycloak_user = await keycloak.get_user(client, user_uuid)

        if keycloak_user is None or not keycloak_user.id:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail=f"User '{user_uuid}' not found"
            )

        await users.modify_user_group(client, user_uuid, keycloak_user.groups, group_to_update, "PUT")

    except (VaultError, APISIXError, KeycloakError) as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e)) from e

    return MessageResponse(message="OK")


@router.put("/admin/users/{user_uuid}/remove-group", response_model=MessageResponse)
async def remove_user_from_group(
    user_uuid: str,
    user_group: UserGroup = Body(...),
    token: AccessToken = Depends(validate_admin_role),
    client: AsyncClient = Depends(get_http_client),
) -> MessageResponse:
    """
    Removes a user from the given group in Keycloak.
    If user has existing API key, the group will be removed accordingly.

    Args:
        user_uuid (str): The UUID of the user.
        user_group (UserGroup): The group from which the user will be removed.
        token (AccessToken): The access token of the user making the request.
        client (AsyncClient): The HTTP client to use for making requests.

    Returns:
        JSONResponse: A response indicating whether the operation was successful.

    Raises:
        HTTPException: If there is an error communicating with Keycloak, Vault or APISIX.
    """
    admin_uuid = token.sub

    logger.info(
        "Admin '%s' requested removing user '%s' from group '%s'",
        admin_uuid,
        user_uuid,
        user_group.group_name,
    )

    try:
        groups = await keycloak.get_groups(client)

        if (
            group := next((group for group in groups if group.name == user_group.group_name), None)
        ) is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Group '{user_group.group_name}' not found",
            )

        keycloak_user = await keycloak.get_user(client, user_uuid)

        if keycloak_user is None or not keycloak_user.id:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail=f"User '{user_uuid}' not found"
            )

        await users.modify_user_group(client, user_uuid, group, "DELETE")

    except (VaultError, APISIXError, KeycloakError) as e:
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail=str(e)) from e

    return MessageResponse(message="OK")
