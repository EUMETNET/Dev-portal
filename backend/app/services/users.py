"""
Business logic for users handlers
"""

from typing import Literal
import asyncio
from httpx import AsyncClient
from app.config import logger
from app.exceptions import KeycloakError
from app.services import apikey, keycloak
from app.models.keycloak import User as KeycloakUser
from app.models.request import User


async def delete_or_disable_user(
    client: AsyncClient, user_uuid: str, action: Literal["DISABLE", "DELETE"]
) -> None:
    """
    Deletes first user's API key from Vault and APISIX(es).
    Then deletes or disables the user from Keycloak based on required action.
    If there is an error while deleting the user from Keycloak,
    the user's API key is rolled back to Vault and APISIX(es).

    Args:
        client (AsyncClient): The HTTP client to use for making requests.
        user_uuid (str): The str UUID of the user to be deleted.
        action (Literal["DISABLE", "DELETE"]): The action to perform on the user.

    Raises:
        KeycloakError: If there is an error while deleting the user from Keycloak.
    """

    user = User(id=user_uuid, groups=[])

    vault_user, apisix_users = await apikey.get_user_from_vault_and_apisixes(client, user.id)
    if vault_user or any(apisix_users):
        logger.debug(
            "User '%s' found in Vault and/or APISIX --> Deleting user from those",
            user.id,
        )
        await apikey.delete_user_from_vault_and_apisixes(client, user, vault_user, apisix_users)

    logger.debug("User '%s' found in Keycloak --> Deleting user", user_uuid)
    try:
        if action == "DISABLE":
            # Mark the user as disabled
            keycloak_user = KeycloakUser(enabled=False)
            await keycloak.update_user(client, user_uuid, keycloak_user)
        elif action == "DELETE":
            await keycloak.delete_user(client, user_uuid)

    except KeycloakError as e:
        logger.warning("Attempting to rollback the user's API key back to Vault and APISIX(es)...")

        await asyncio.gather(
            apikey.handle_rollback(
                client,
                user,
                vault_user,
                [apisix_user for apisix_user in apisix_users if apisix_user],
                rollback_from="DELETE",
            ),
        )

        raise KeycloakError("Keycloak service error") from e
