"""
Business logic for users handlers
"""

from typing import cast
import asyncio
from httpx import AsyncClient
from app.config import logger
from app.exceptions import KeycloakError, APISIXError
from app.services import apikey, keycloak
from app.utils.uuid import remove_dashes
from app.models.apisix import APISixConsumer


async def delete_user(client: AsyncClient, user_uuid: str) -> None:
    """
    Deletes first user's API key from Vault and APISIX(es).
    Then deletes the user from Keycloak.
    If there is an error while deleting the user from Keycloak,
    the user's API key is rolled back to Vault and APISIX(es).

    Args:
        client (AsyncClient): The HTTP client to use for making requests.
        user_uuid (str): The str UUID of the user to be deleted.

    Raises:
        KeycloakError: If there is an error while deleting the user from Keycloak.
    """
    user_uuid_no_dashes = remove_dashes(user_uuid)

    vault_user, apisix_users = await apikey.get_user_from_vault_and_apisixes(
        client, user_uuid_no_dashes
    )
    if vault_user or any(apisix_users):
        logger.debug(
            "User '%s' found in Vault and/or APISIX --> Deleting user from those",
            user_uuid_no_dashes,
        )
        await apikey.delete_user_from_vault_and_apisixes(
            client, user_uuid_no_dashes, vault_user, apisix_users
        )

    keycloak_user = await keycloak.get_user(client, user_uuid)

    if keycloak_user:
        logger.debug("User '%s' found in Keycloak --> Deleting user", user_uuid)
        try:
            await keycloak.delete_user(client, user_uuid)

        except KeycloakError as e:
            logger.warning(
                "Attempting to rollback the user's API key back to Vault and APISIX(es)..."
            )

            apisix_users, instance_names = map(
                list,
                zip(*((user, user.instance_name) for user in apisix_users if user is not None)),
            )
            await asyncio.gather(
                apikey.handle_rollback(
                    client,
                    user_uuid_no_dashes,
                    vault_user,
                    cast(list[APISixConsumer | APISIXError], apisix_users),
                    instance_names,
                    rollback_from="DELETE",
                ),
            )

            raise KeycloakError("Keycloak service error") from e
