"""
Business logic for users handlers
"""

from typing import Literal
import asyncio
from httpx import AsyncClient
from app.config import logger
from app.exceptions import KeycloakError
from app.services import apikey, keycloak, apisix
from app.models.keycloak import User as KeycloakUser
from app.models.request import User
from app.models.apisix import APISixConsumer
from app.exceptions import APISIXError


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


async def promote_user_to_group(client: AsyncClient, user_uuid: str, group_uuid: str) -> None:
    """
    Promotes a user to a group in Keycloak.
    If user has existing API key it will be promoted to the corresponding group in APISIX(es).

    Args:
        client (AsyncClient): The HTTP client to use for making requests.
        user_uuid (str): The UUID of the user to promote.
        group (str): The group to promote the user to.

    Raises:
        KeycloakError: If there is an error while promoting the user to the group.
    """

    try:
        await keycloak.modify_user_group_membership(client, user_uuid, group_uuid, "PUT")

        user = User(id=user_uuid, groups=[group_uuid])

        _vault_user, apisix_users = await apikey.get_user_from_vault_and_apisixes(client, user.id)

        if any(apisix_users):
            logger.debug(
                "User '%s' found in APISIX(es) -->"
                "Moving user's API key to group '%s' in APISIX(es)",
                user_uuid,
                group_uuid,
            )

            apisix_responses: list[APISixConsumer | APISIXError] = await asyncio.gather(
                *apisix.create_tasks(
                    apisix.upsert_apisix_consumer,
                    client,
                    user,
                ),
                return_exceptions=True,
            )

            if any(isinstance(response, APISIXError) for response in apisix_responses):
                logger.warning("Attempting to rollback the successfull APISIX operation(s)...")

                # We want to rollback the user's state to before the group was altered
                rollback_from_delete: list[APISixConsumer | APISIXError] = []

                rollback_from_create: list[APISixConsumer | APISIXError] = []

                for apisix_user, response in zip(apisix_users, apisix_responses):
                    # user was already in this instance so restore the previous state
                    if apisix_user and isinstance(response, APISixConsumer):
                        rollback_from_delete.append(apisix_user)
                    # user was not in this instance so delete the newly created user
                    # to restore the previous state
                    elif apisix_user is None and isinstance(response, APISixConsumer):
                        rollback_from_create.append(response)

                if rollback_from_delete:
                    await apikey.handle_rollback(
                        client,
                        user,
                        None,
                        rollback_from_delete,
                        rollback_from="DELETE",
                    )

                if rollback_from_create:
                    await apikey.handle_rollback(
                        client,
                        user,
                        None,
                        rollback_from_create,
                        rollback_from="CREATE",
                    )

                logger.info("Rollback operation completed successfully")
                raise APISIXError("APISIX service error")

    except KeycloakError as e:
        raise KeycloakError("Keycloak service error") from e
