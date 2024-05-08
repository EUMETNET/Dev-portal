"""
Service for interacting with the Keycloak.
"""

from urllib.parse import urlparse
from aiocache import cached, Cache  # type: ignore
from httpx import AsyncClient, HTTPError
from app.config import settings, logger
from app.dependencies.http_client import http_request
from app.exceptions import KeycloakError
from app.models.keycloak import TokenResponse, User

config = settings()

# Keycloak access token ttl is 5 mins. subtract 10 seconds to account for possible time skew
TTL = 60 * 5 - 10


def extract_uuid_from_url(url: str) -> str:
    """
    Extract the uuid from the url.
    Expects the uuid to be the last part of the url.
    """
    return urlparse(url).path.split("/")[-1]


@cached(cache=Cache.MEMORY, ttl=TTL, key="service_account_token")
async def get_service_account_token(client: AsyncClient) -> str:
    """
    Get a service account token from Keycloak.

    This function gets a token from Keycloak using the client credentials flow.

    Returns:
        str: The token from Keycloak.

    Raises:
        KeycloakError: If there is an HTTP error while getting the token.
    """
    try:
        token_url = (
            f"{config.keycloak.url}/realms/{config.keycloak.realm}/protocol/openid-connect/token"
        )
        data = {
            "client_id": config.keycloak.client_id,
            "client_secret": config.keycloak.client_secret,
            "grant_type": "client_credentials",
        }

        response = await http_request(client, "POST", token_url, data=data)

        return TokenResponse(**response.json()).access_token

    except HTTPError as e:
        logger.exception("Error retrieving Keycloak service account token.")
        raise KeycloakError("Keycloak service error") from e


async def get_user(client: AsyncClient, user_uuid: str) -> User | None:
    """
    Get a user from Keycloak.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        user_uuid (str): The UUID of the user to get.

    Returns:
        dict[str, Any]: The user information.

    Raises:
        KeycloakError: If there is an HTTP error while getting the user.
    """
    try:
        token = await get_service_account_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        user_url = f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/users/{user_uuid}"
        response = await http_request(
            client, "GET", user_url, headers=headers, valid_status_codes=(200, 404)
        )

        return User(**response.json()) if response.status_code == 200 else None
    except HTTPError as e:
        logger.exception("Error getting user '%s' from Keycloak.", user_uuid)
        raise KeycloakError("Keycloak service error") from e


async def create_user(client: AsyncClient, user: User) -> str:
    """
    Create a user in Keycloak.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        user (dict[str, Any]): The user information to create.

    Returns:
        str: The user uuid.

    Raises:
        KeycloakError: If there is an HTTP error while creating the user.
    """
    try:
        token = await get_service_account_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        users_url = f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/users"

        response = await http_request(
            client, "POST", users_url, headers=headers, json=user.model_dump()
        )
        # Keycloak provides the user location in headers which contains the uuid
        return extract_uuid_from_url(response.headers["location"])
    except HTTPError as e:
        logger.exception("Error creating user '%s' to Keycloak.", user)
        raise KeycloakError("Keycloak service error") from e


async def delete_user(client: AsyncClient, user_uuid: str) -> None:
    """
    Delete a user from Keycloak.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        user_uuid (str): The UUID of the user to delete.

    Raises:
        KeycloakError: If there is an HTTP error while deleting the user.
    """
    try:
        token = await get_service_account_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        user_url = f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/users/{user_uuid}"
        await http_request(client, "DELETE", user_url, headers=headers)
    except HTTPError as e:
        logger.exception("Error deleting user with id '%s' from Keycloak.", user_uuid)
        raise KeycloakError("Keycloak service error") from e


async def update_user(client: AsyncClient, user_uuid: str, user: User) -> User:
    """
    Updates a user in Keycloak.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        user_uuid (str): The UUID of the user to update.
        user (dict[str, Any]): The user information to update.

    Returns:
        dict[str, Any]: The user information.

    Raises:
        KeycloakError: If there is an HTTP error while updating the user.
    """
    try:
        token = await get_service_account_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        users_url = f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/users/{user_uuid}"

        # Keycloak returns 200 OK
        # https://www.keycloak.org/docs-api/22.0.1/rest-api/index.html#_users
        await http_request(client, "PUT", users_url, headers=headers, json=user.model_dump())
        return user
    except HTTPError as e:
        logger.exception("Error creating user '%s' to Keycloak.", user)
        raise KeycloakError("Keycloak service error") from e
