"""
Business logic for API key handlers
"""

import asyncio
from typing import cast, Literal, Coroutine, Any
from httpx import AsyncClient
from app.config import logger
from app.models.vault import VaultUser
from app.models.apisix import APISixConsumer
from app.exceptions import APISIXError, VaultError
from app.services import vault, apisix


async def get_user_from_vault_and_apisixes(
    client: AsyncClient, uuid_not_dashes: str
) -> tuple[VaultUser | None, list[APISixConsumer | None]]:
    """
    Retrieve user information from Vault and APISIX instances.

    Sends requests to Vault and APISIX instance(s) to retrieve user information.
    In case of any exceptions during these requests,
    they are logged and the first occurred error is raised as an HTTPException.

    Args:
        client (AsyncClient): The HTTP client used for making requests.
        uuid_not_dashes (str): The user's UUID, formatted without dashes.

    Returns:
        tuple[VaultUser | None, list[APISixConsumer | None]]:
            A tuple containing the user's information from Vault
            and a list of APISixConsumers from APISIX instances.

    Raises:
        HTTPException: From the service where the first error occurred in
            Either Vault or APISIX.
    """

    results = await asyncio.gather(
        vault.get_user_info_from_vault(client, uuid_not_dashes),
        *apisix.create_tasks(apisix.get_apisix_consumer, client, uuid_not_dashes),
        return_exceptions=True,
    )

    if error := next(
        (error for error in results if isinstance(error, (APISIXError, VaultError))), None
    ):
        raise error

    # Stupid to use cast here but mypy does not seem to understand
    # that we are not returning BaseException nor derived classes
    return cast(VaultUser | None, results[0]), cast(list[APISixConsumer | None], results[1:])


# pylint: disable=too-many-arguments
async def handle_rollback(
    client: AsyncClient,
    uuid_no_dashes: str,
    vault_user: VaultUser | None,
    apisix_responses: list[APISixConsumer | APISIXError],
    apisix_instances: list[str],
    rollback_from: Literal["CREATE", "DELETE"],
) -> None:
    """
    Rollback the state of the system in case of an error.

    This function is called in case of an error during the creation or deletion of a user.
    It is used to rollback the state of the system to its previous state (=state before request).

    Args:
        client: The HTTP client to use for making the request.
        uuid_no_dashes (str): The UUID of the user, without dashes.
        vault_user (VaultUser | None): The VaultUser object, or None if the user does not exist.
        apisix_responses (list[APISixConsumer | Exception]): A list of responses from APISIX,
            which can be either APISixConsumer objects or Exceptions.
        apisix_instances (list[str]): A list of APISIX instances.
        rollback_from (Literal["CREATE", "DELETE"]): The operation to rollback from.

    Raises:
        HTTPException: If there is an error during the rollback process.
    """
    tasks: list[Coroutine[Any, Any, VaultUser | None | APISixConsumer]] = []

    if vault_user:
        if rollback_from == "CREATE":
            tasks.append(vault.delete_user_from_vault(client, uuid_no_dashes))
        else:
            tasks.append(vault.save_user_to_vault(client, uuid_no_dashes, vault_user))

    not_errored_apisix_instances = [
        instance
        for instance, response in zip(apisix_instances, apisix_responses)
        if not isinstance(response, APISIXError)
    ]

    if rollback_from == "CREATE":
        tasks.extend(
            apisix.create_tasks(
                apisix.delete_apisix_consumer,
                client,
                uuid_no_dashes,
                instances=not_errored_apisix_instances,
            )
        )
    else:
        tasks.extend(
            apisix.create_tasks(
                apisix.create_apisix_consumer,
                client,
                uuid_no_dashes,
                instances=not_errored_apisix_instances,
            )
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    if error := next(
        (error for error in results if isinstance(error, (APISIXError, VaultError))), None
    ):
        raise error


async def create_user_to_vault_and_apisixes(
    client: AsyncClient,
    uuid_no_dashes: str,
    vault_user: VaultUser | None,
    apisix_users: list[APISixConsumer | None],
) -> VaultUser:
    """
    Creates a user in Vault and APISIX instances if they do not already exist.

    This function checks if a user exists in Vault and in the APISIX instances.
    If the user does not exist in Vault, it saves the user to Vault.
    If the user does not exist in any of the APISIX instances,
        it creates the user in those instances.

    Args:
        client (AsyncClient): The HTTP client used for making requests.
        uuid_no_dashes (str): The user's UUID, formatted without dashes.
        vault_user (VaultUser | None): The user's information from Vault,
            or None if the user does not exist in Vault.
        apisix_users (list[APISixConsumer | None]): A list of the user's information
            from each APISIX instance, or None for instances where the user does not exist.

    Returns:
        VaultUser: The user's information from Vault, either retrieved or newly created.

    Raises:
        APISIXError: If there is an error creating the user in an APISIX instance.
        VaultError: If there is an error saving the user to Vault.
    """
    current_vault_user = vault_user

    if not current_vault_user:
        logger.debug("User '%s' not found in Vault --> Saving user to Vault", uuid_no_dashes)
        current_vault_user = await vault.save_user_to_vault(client, uuid_no_dashes)

    apisix_instances_lack_user = apisix.apisix_instances_missing_user(apisix_users)

    if apisix_instances_lack_user:
        logger.debug(
            "User '%s' not found in following APISIX instances: %s -->"
            "Creating user to these instances",
            uuid_no_dashes,
            ",".join(apisix_instances_lack_user),
        )

        apisix_responses: list[APISixConsumer | APISIXError] = await asyncio.gather(
            *apisix.create_tasks(
                apisix.create_apisix_consumer,
                client,
                uuid_no_dashes,
                instances=apisix_instances_lack_user,
            ),
            return_exceptions=True,
        )

        if any(isinstance(response, APISIXError) for response in apisix_responses):
            logger.warning("Attempting to rollback the successfull operation(s)...")

            await handle_rollback(
                client,
                uuid_no_dashes,
                current_vault_user,
                apisix_responses,
                apisix_instances_lack_user,
                rollback_from="CREATE",
            )

            logger.info("Rollback operation completed successfully")
            raise APISIXError("APISIX service error")

    return current_vault_user


async def delete_user_from_vault_and_apisixes(
    client: AsyncClient,
    uuid_no_dashes: str,
    vault_user: VaultUser | None,
    apisix_users: list[APISixConsumer | None],
) -> None:
    """
    Deletes a user from Vault and APISIX instances.

    This function checks if a user exists in Vault and in the provided APISIX instances.
    If the user exists in Vault, it deletes the user from Vault.
    If the user exists in any of the APISIX instances, it deletes the user from those instances.

    Args:
        client (AsyncClient): The HTTP client used for making requests.
        uuid_no_dashes (str): The user's UUID, formatted without dashes.
        vault_user (VaultUser | None): The user's information from Vault,
            or None if the user does not exist in Vault.
        apisix_users (list[APISixConsumer | None]): A list of the user's information
            from each APISIX instance, or None for instances where the user does not exist.

    Returns:
        None

    Raises:
        APISIXError: If there is an error deleting the user from an APISIX instance.
        VaultError: If there is an error deleting the user from Vault.
    """
    if vault_user:
        logger.debug("User '%s' found in Vault --> Deleting user from Vault", uuid_no_dashes)
        await vault.delete_user_from_vault(client, uuid_no_dashes)

    if apisix_instances_with_user := [user.instance_name for user in apisix_users if user]:
        logger.debug(
            "User '%s' found in following APISIX instances: %s --> Deleting user from those",
            uuid_no_dashes,
            ",".join(apisix_instances_with_user),
        )

        apisix_responses: list[APISixConsumer | APISIXError] = await asyncio.gather(
            *apisix.create_tasks(
                apisix.delete_apisix_consumer,
                client,
                uuid_no_dashes,
                instances=apisix_instances_with_user,
            ),
            return_exceptions=True,
        )

        if any(isinstance(response, APISIXError) for response in apisix_responses):
            logger.warning("Attempting to rollback the successfull operation(s)...")

            await handle_rollback(
                client,
                uuid_no_dashes,
                vault_user,
                apisix_responses,
                apisix_instances_with_user,
                rollback_from="DELETE",
            )

            logger.info(
                "Rollback operation completed successfully. Returning error response to client."
            )
            raise APISIXError("APISIX service error")
