"""
Business logic for API key handlers
"""

import asyncio
from typing import cast, Literal, Coroutine, Any, Sequence
from httpx import AsyncClient
from app.config import logger, settings
from app.models.request import User
from app.models.vault import VaultUser
from app.models.apisix import APISixConsumer
from app.exceptions import APISIXError, VaultError
from app.services import vault, apisix

config = settings()


async def get_user_from_vault_and_apisix_instances(
    client: AsyncClient, uuid_not_dashes: str
) -> tuple[list[VaultUser | None], list[APISixConsumer | None]]:
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

    vault_tasks = vault.create_tasks(vault.get_user_info_from_vault, client, uuid_not_dashes)

    results = await asyncio.gather(
        *vault_tasks,
        *apisix.create_tasks(apisix.get_apisix_consumer, client, uuid_not_dashes),
        return_exceptions=True,
    )

    if error := next(
        (error for error in results if isinstance(error, (APISIXError, VaultError))), None
    ):
        raise error

    # Stupid to use cast here but mypy does not seem to understand
    # that we are not returning BaseException nor derived classes
    return cast(list[VaultUser | None], results[: len(vault_tasks)]), cast(
        list[APISixConsumer | None], results[len(vault_tasks) :]
    )


# pylint: disable=too-many-arguments
async def handle_rollback(
    client: AsyncClient,
    user: User,
    responses: Sequence[VaultUser | VaultError | APISixConsumer | APISIXError],
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
    tasks: list[Coroutine[Any, Any, VaultUser | APISixConsumer]] = []

    # if vault_user:
    #    if rollback_from == "CREATE":
    #        tasks.append(vault.delete_user_from_vault(client, user.id))
    #    else:
    #        tasks.append(vault.save_user_to_vault(client, user.id, vault_user))

    if rollback_from == "CREATE":
        not_errored_vault_instances = [
            user.instance_name for user in responses if isinstance(user, VaultUser)
        ]

        not_errored_apisix_instances = [
            user.instance_name for user in responses if isinstance(user, APISixConsumer)
        ]

        # not_errored_vault_instances = [
        #    vault_user.instance_name
        #    for vault_user in vault_responses
        #    if not isinstance(vault_user, VaultError)
        # ]
        # not_errored_apisix_instances = [
        #    consumer.instance_name
        #    for consumer in apisix_responses
        #    if not isinstance(consumer, APISIXError)
        # ]
        # tasks.extend(
        #    apisix.create_tasks(
        #        apisix.delete_apisix_consumer,
        #        client,
        #        user,
        #        instances=not_errored_apisix_instances,
        #    )
        # )
        tasks = [
            *vault.create_tasks(
                vault.delete_user_from_vault,
                client,
                user.id,
                instances=not_errored_vault_instances,
            ),
            *apisix.create_tasks(
                apisix.delete_apisix_consumer,
                client,
                user,
                instances=not_errored_apisix_instances,
            ),
        ]
    else:
        existing_vault_users = {
            user.instance_name: user for user in responses if isinstance(user, VaultUser)
        }
        existing_apisix_consumers = {
            user.instance_name: user for user in responses if isinstance(user, APISixConsumer)
        }
        tasks = [
            *vault.create_tasks(
                vault.save_user_to_vault,
                client,
                users=existing_vault_users,
            ),
            *apisix.create_tasks(
                apisix.upsert_apisix_consumer,
                client,
                consumers=existing_apisix_consumers,
            ),
        ]
        # tasks.extend(
        #    apisix.create_tasks(
        #        apisix.upsert_apisix_consumer,
        #        client,
        #        consumers=existing_consumers,
        #    )
        # )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    if error := next(
        (error for error in results if isinstance(error, (APISIXError, VaultError))), None
    ):
        raise error


async def create_user_to_vault_and_apisixes(
    client: AsyncClient,
    user: User,
    vault_users: list[VaultUser | None],
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
    # User has same API key in all Vault instances so grab the first one as base
    logger.info("V USers %s", vault_users)
    vault_user = next(
        (
            VaultUser(
                auth_key=vault_user.auth_key,
                date=vault_user.date,
                id=vault_user.id,
                instance_name="",
            )
            for vault_user in vault_users
            if vault_user
        ),
        VaultUser(
            auth_key=vault.generate_api_key(user.id),
            date=vault.get_formatted_str_date("%Y/%m/%d %H:%M:%S"),
            id=user.id,
            instance_name="",
        ),
    )

    tasks: list[Coroutine[Any, Any, VaultUser | APISixConsumer]] = []

    if None in vault_users:
        logger.debug(
            "User '%s' not found in all Vault instances --> "
            "Upserting user to Vault instances: %s",
            user.id,
            ", ".join([instance.name for instance in config.vault.instances]),
        )
        tasks.extend(vault.create_tasks(vault.save_user_to_vault, client, vault_user))
        # vault_responses = list[VaultUser | VaultError] = await asyncio.gather(
        #    *vault.create_tasks(vault.save_user_to_vault, client, user.id, vault_user),
        #    return_exceptions=True,
        # )

        # current_vault_user = await vault.save_user_to_vault(client, user.id)

    # apisix_instances_lack_user = apisix.apisix_instances_missing_user(apisix_users)

    if None in apisix_users:
        logger.debug(
            "User '%s' not found in all APISIX instances --> "
            "Creating or updating user to APISIX instances: %s",
            user.id,
            ", ".join([instance.name for instance in config.apisix.instances]),
        )

        tasks.extend(
            apisix.create_tasks(
                apisix.upsert_apisix_consumer,
                client,
                user,
            )
        )

        # apisix_responses: list[APISixConsumer | APISIXError] = await asyncio.gather(
        #    *apisix.create_tasks(
        #        apisix.upsert_apisix_consumer,
        #        client,
        #        user,
        #    ),
        #    return_exceptions=True,
        # )

    responses = cast(
        list[VaultUser | APISixConsumer | VaultError | APISIXError],
        await asyncio.gather(*tasks, return_exceptions=True),
    )

    if error := next(
        (response for response in responses if isinstance(response, (APISIXError, VaultError))),
        None,
    ):
        logger.warning("Attempting to rollback the successfull operation(s)...")

        await handle_rollback(
            client,
            user,
            responses,
            rollback_from="CREATE",
        )

        logger.info("Rollback operation completed successfully")
        raise error

    return vault_user


async def delete_user_from_vault_and_apisixes(
    client: AsyncClient,
    user: User,
    vault_users: list[VaultUser | None],
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
    tasks: list[Coroutine[Any, Any, VaultUser | APISixConsumer]] = []

    for u in vault_users:
        logger.debug("Vault user: %s", u)

    if vault_instances_with_user := [user.instance_name for user in vault_users if user]:
        logger.debug(
            "User '%s' found in following Vault instances: %s --> Deleting user from those",
            user.id,
            vault_instances_with_user,
        )
        # await vault.delete_user_from_vault(client, user.id)

        # We can use the first user as the API key is the same for all instances
        common_vault_user = next(user for user in vault_users if user)
        tasks.extend(
            vault.create_tasks(
                vault.delete_user_from_vault,
                client,
                common_vault_user,
                instances=vault_instances_with_user,
            )
        )

    if apisix_instances_with_user := [user.instance_name for user in apisix_users if user]:
        logger.debug(
            "User '%s' found in following APISIX instances: %s --> Deleting user from those",
            user.id,
            ",".join(apisix_instances_with_user),
        )

        # apisix_responses: list[APISixConsumer | APISIXError] = await asyncio.gather(
        #    *apisix.create_tasks(
        #        apisix.delete_apisix_consumer,
        #        client,
        #        user,
        #        instances=apisix_instances_with_user,
        #    ),
        #    return_exceptions=True,
        # )

        tasks.extend(
            apisix.create_tasks(
                apisix.delete_apisix_consumer,
                client,
                user,
                instances=apisix_instances_with_user,
            )
        )

        responses = cast(
            list[VaultUser | APISixConsumer | VaultError | APISIXError],
            await asyncio.gather(*tasks, return_exceptions=True),
        )

        if error := next(
            (response for response in responses if isinstance(response, (VaultError, APISIXError))),
            None,
        ):
            logger.warning("Attempting to rollback the successfull operation(s)...")

            await handle_rollback(
                client,
                user,
                responses,
                rollback_from="DELETE",
            )

            logger.info(
                "Rollback operation completed successfully. Returning error response to client."
            )
            raise error
