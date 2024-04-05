"""
Service for interacting with the Vault.
"""

import hashlib
from datetime import datetime, timezone
from httpx import AsyncClient, HTTPError
from app.config import settings, logger
from app.dependencies.http_client import http_request
from app.models.vault import VaultUser
from app.exceptions import VaultError

config = settings()


def get_formatted_str_date(format_str: str) -> str:
    """
    Get the current datetime in UTC formatted as a string.

    Args:
        format (str): The format to use for the datetime string.

    Returns:
        str: The current datetime in UTC, formatted as a string.
    """
    return datetime.now(timezone.utc).strftime(format_str)


def generate_api_key(identifier: str) -> str:
    """
    Generate an API key using the given identifier.

    The API key is generated by concatenating the current date (formatted as "%Y%m%d"),
    the identifier, and a secret phase, and then hashing this string using MD5.

    Args:
        identifier (str): The identifier to use in the generation of the API key.

    Returns:
        str: The generated API key, represented as a hexadecimal string.
    """
    formatted_date = get_formatted_str_date("%Y%m%d")

    secret_phase = config.vault.secret_phase
    logger.debug("Current Date: %s", formatted_date)
    logger.debug("Login identifier: %s", identifier)
    logger.debug("Secret Phase: %s", secret_phase)

    sha256 = hashlib.sha256()
    sha256.update((formatted_date + identifier + secret_phase).encode())
    api_key = sha256.hexdigest()
    logger.debug("Generated API key: %s", api_key)

    return api_key


async def save_user_to_vault(
    client: AsyncClient, identifier: str, user: VaultUser | None = None
) -> VaultUser:
    """
    Save a user to Vault.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the user.

    Returns:
        VaultUser: A dictionary representing the saved user.

    Raises:
        VaultError: If there is an HTTP error while creating the user.
    """
    if not user:
        generated_api_key = generate_api_key(identifier)

        vault_user = VaultUser(
            auth_key=generated_api_key, date=get_formatted_str_date("%Y/%m/%d %H:%M:%S")
        )
    else:
        vault_user = user

    try:
        await http_request(
            client,
            "POST",
            f"{config.vault.url}/v1/{config.vault.base_path}/{identifier}",
            headers={"X-Vault-Token": config.vault.token},
            data=vault_user.model_dump(),
        )
        logger.info("Saved user '%s' to Vault", identifier)
        return vault_user
    except HTTPError as e:
        logger.exception("Error saving user '%s' to Vault", identifier)
        raise VaultError("Vault service error") from e


async def get_user_info_from_vault(client: AsyncClient, identifier: str) -> VaultUser | None:
    """
    Retrieve a user's information from Vault.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
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
        url = f"{config.vault.url}/v1/{config.vault.base_path}/{identifier}"
        headers = {"X-Vault-Token": config.vault.token}
        response = await http_request(
            client, "GET", url, headers=headers, valid_status_codes=(200, 404)
        )
        return VaultUser(**response.json()["data"]) if response.status_code == 200 else None
    except HTTPError as e:
        logger.exception("Error retrieving user '%s' from Vault", identifier)
        raise VaultError("Vault service error") from e


async def delete_user_from_vault(client: AsyncClient, identifier: str) -> None:
    """
    Delete a user from Vault.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the user.

    Raises:
        VaultError: If there is an HTTP error while deleting the user.
    """
    try:
        await http_request(
            client,
            "DELETE",
            f"{config.vault.url}/v1/{config.vault.base_path}/{identifier}",
            headers={"X-Vault-Token": config.vault.token},
        )
        logger.info("Deleted user '%s' from Vault", identifier)
    except HTTPError as e:
        logger.exception("Error deleting user '%s' from Vault", identifier)
        raise VaultError("Vault service error") from e


async def healthcheck(client: AsyncClient) -> str:
    """
    Check the health of the Vault service.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.

    Raises:
        VaultError: If there is an HTTP error while checking the health of the service.
    """
    try:
        # https://developer.hashicorp.com/vault/api-docs/system/health
        _response = await http_request(client, "GET", f"{config.vault.url}/v1/sys/health")
        return "OK"
    except HTTPError as e:
        logger.exception("Error checking health of Vault service")
        raise VaultError("Vault service error") from e
