"""
Service for interacting with the Vault.
"""

from httpx import AsyncClient, HTTPError
from app.config import logger
from app.dependencies.http_client import http_request
from app.models.vault import VaultUser
from app.config import VaultInstanceSettings
from app.exceptions import VaultError


async def save_user_to_vault(
    client: AsyncClient,
    instance: VaultInstanceSettings,
    user: VaultUser,
) -> VaultUser:
    """
    Upsert a user to Vault.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        user (VaultUser): The user object to save to Vault.

    Returns:
        VaultUser: A dictionary representing the saved user.

    Raises:
        VaultError: If there is an HTTP error while creating the user.
    """

    try:
        await http_request(
            client,
            "POST",
            f"{instance.url}/v1/{instance.base_path}/{user.id}",
            headers={"X-Vault-Token": instance.token},
            json=user.model_dump(exclude={"instance_name", "id"}),
        )
        logger.info("Saved user '%s' to Vault instance %s", user.id, instance.url)
        return VaultUser(
            auth_key=user.auth_key,
            date=user.date,
            id=user.id,
        )
    except HTTPError as e:
        logger.exception("Error saving user '%s' to Vault instance %s", user.id, instance.url)
        raise VaultError("Vault service error") from e


async def get_user_info_from_vault(
    client: AsyncClient, instance: VaultInstanceSettings, identifier: str
) -> VaultUser | None:
    """
    Retrieve a user's information from Vault.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        instance: (VaultInstanceSettings): The Vault instace where Vault is read from
        identifier (str): The identifier for the user.

    Returns:
        VaultUser: A dictionary representing the user if found, None otherwise.

    Raises:
        VaultError: If there is an HTTP error while retrieving the user.
            404 Not Found is not considered as an error.
    """
    # response looks e.g. like this
    # {'request_id': '2e1de3e3-6f3b-ccc6-28ae-20bc1b620b4f',
    #'lease_id': '', 'renewable': False, 'lease_duration': 2764800,
    #'data': {'as': 'as', 'dfdf': 'dfdf'}, 'wrap_info': None, 'warnings': None, 'auth': None}
    try:
        url = f"{instance.url}/v1/{instance.base_path}/{identifier}"
        headers = {"X-Vault-Token": instance.token}
        response = await http_request(
            client, "GET", url, headers=headers, valid_status_codes=(200, 404)
        )
        return (
            VaultUser(
                auth_key=response.json()["data"]["auth_key"],
                date=response.json()["data"]["date"],
                id=identifier,
            )
            if response.status_code == 200
            else None
        )
    except HTTPError as e:
        logger.exception(
            "Error retrieving user '%s' from Vault instance %s", identifier, instance.url
        )
        raise VaultError("Vault service error") from e


async def list_user_identifiers_from_vault(
    client: AsyncClient, instance: VaultInstanceSettings
) -> list[str | None]:
    """
    Retrieve a user's identifiers from base path.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the user.

    Returns:
        list[str | None]: A list containing Vaultuser identifiers

    Raises:
        VaultError: If there is an HTTP error while retrieving the user.
            404 Not Found is not considered as an error.
    """
    # response looks e.g. like this
    # {'request_id': '2e1de3e3-6f3b-ccc6-28ae-20bc1b620b4f',
    #'lease_id': '', 'renewable': False, 'lease_duration': 2764800,
    #'data': {'as': 'as', 'dfdf': 'dfdf'}, 'wrap_info': None, 'warnings': None, 'auth': None}
    try:
        url = f"{instance.url}/v1/{instance.base_path}/"
        headers = {"X-Vault-Token": instance.token}
        response = await http_request(
            client, "LIST", url, headers=headers, valid_status_codes=(200, 404)
        )
        return response.json()["data"].get("keys", []) if response.status_code == 200 else []
    except HTTPError as e:
        logger.exception("Error retrieving user identifiers from Vault instance %s", instance.url)
        raise VaultError("Vault service error") from e
