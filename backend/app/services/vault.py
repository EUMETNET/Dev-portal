"""
Service for interacting with the Vault.
"""

import hashlib
from datetime import datetime, timezone
from httpx import AsyncClient
from app.config import settings, logger
from app.dependencies.http_client import http_request
from app.models.vault import VaultUser

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


async def save_user_to_vault(client: AsyncClient, identifier: str) -> VaultUser:
    """
    Save a user to Vault.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the user.

    Returns:
        VaultUser: A dictionary representing the saved user.
    """
    generated_api_key = generate_api_key(identifier)

    vault_user = VaultUser(
        auth_key=generated_api_key, date=get_formatted_str_date("%Y/%m/%d %H:%M:%S")
    )

    await http_request(
        client,
        "POST",
        f"{config.vault.url}/v1/{config.vault.base_path}/{identifier}",
        headers={"X-Vault-Token": config.vault.token},
        data=vault_user.model_dump(),
    )

    return vault_user


async def get_user_info_from_vault(client: AsyncClient, identifier: str) -> VaultUser | None:
    """
    Retrieve a user's information from Vault.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the user.

    Returns:
        VaultUser: A dictionary representing the user if found, None otherwise.
    """
    # response looks e.g. like this
    # {'request_id': '2e1de3e3-6f3b-ccc6-28ae-20bc1b620b4f',
    #'lease_id': '', 'renewable': False, 'lease_duration': 2764800,
    #'data': {'as': 'as', 'dfdf': 'dfdf'}, 'wrap_info': None, 'warnings': None, 'auth': None}

    url = f"{config.vault.url}/v1/{config.vault.base_path}/{identifier}"
    headers = {"X-Vault-Token": config.vault.token}
    response = await http_request(
        client, "GET", url, headers=headers, valid_status_codes=(200, 404)
    )
    return VaultUser(**response.json()["data"]) if response.status_code == 200 else None


async def delete_user_from_vault(client: AsyncClient, identifier: str) -> None:
    """
    Delete a user from Vault.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the user.
    """
    await http_request(
        client,
        "DELETE",
        f"{config.vault.url}/v1/{config.vault.base_path}/{identifier}",
        headers={"X-Vault-Token": config.vault.token},
    )
