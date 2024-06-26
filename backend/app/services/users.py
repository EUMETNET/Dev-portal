"""
Business logic for users handlers
"""

from typing import Literal
import asyncio
from httpx import AsyncClient
from app.config import logger
from app.exceptions import KeycloakError
from app.services import apikey, keycloak, apisix
from app.models.keycloak import User as KeycloakUser, Group
from app.models.request import User
from app.models.apisix import APISixConsumer
from app.exceptions import APISIXError


async def delete_or_disable_user(
    client: AsyncClient,
    user_uuid: str,
    keycloak_user: KeycloakUser,
    action: Literal["DISABLE", "DELETE"],
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

    log_action = "Disabling" if action == "DISABLE" else "Deleting"

    vault_user, apisix_users = await apikey.get_user_from_vault_and_apisixes(client, user.id)
    if vault_user or any(apisix_users):
        logger.debug(
            "User '%s' found in Vault and/or APISIX --> %s user from those",
            user_uuid,
            log_action,
        )
        await apikey.delete_user_from_vault_and_apisixes(client, user, vault_user, apisix_users)

    logger.debug("User '%s' found in Keycloak --> %s user", user_uuid, log_action)

    try:
        if action == "DISABLE":
            # Mark the user as disabled
            keycloak_user.enabled = False
            await keycloak.update_user(client, user_uuid, keycloak_user)
        elif action == "DELETE":
            await keycloak.delete_user(client, user_uuid)

    except KeycloakError as e:
        logger.warning("Attempting to rollback the user's API key back to Vault and APISIX(es)...")

        if any(isinstance(apisix_user, APISixConsumer) for apisix_user in apisix_users):
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


async def modify_user_group(
    client: AsyncClient, user_uuid: str, group: Group, action: Literal["PUT", "DELETE"]
) -> None:
    """
    Add or remove a user from a given group in Keycloak.
    If the user has an existing API key,
    it will be either added to or removed from a given group based on the given action.

    Args:
        client (AsyncClient): The HTTP client to use for making requests.
        user_uuid (str): The UUID of the user.
        group_uuid (str): The UUID of the group to add/remove the user from.
        action (Literal["PUT", "DELETE"]): The action to perform on the user's group membership.

    Raises:
        KeycloakError: If there is an error while adding/removing the user to the group.
        APISIXError: If there is an error while adding/removing the user's API key
        to given group in APISIX.
    """

    try:
        await keycloak.modify_user_group_membership(client, user_uuid, group.id, action)

        user_groups = [group.name] if action == "PUT" else []

        user = User(id=user_uuid, groups=user_groups)

        _vault_user, apisix_users = await apikey.get_user_from_vault_and_apisixes(client, user.id)

        if any(apisix_users):
            log_action = (
                "Updating user's API key to" if action == "PUT" else "Removing user's API key from"
            )
            logger.debug(
                "User '%s' found in APISIX(es) --> %s group '%s' in APISIX(es)",
                user_uuid,
                log_action,
                group.name,
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
                logger.warning(
                    "Attempting to rollback the successfull Keycloak and APISIX operation(s)..."
                )

                # Rollback the user's group membership in Keycloak
                await keycloak.modify_user_group_membership(
                    client, user_uuid, group.id, "DELETE" if action == "PUT" else "PUT"
                )

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
