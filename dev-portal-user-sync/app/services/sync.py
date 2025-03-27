"""
Validates settings and calls sync functions asynchronously
"""


from httpx import AsyncClient
from app.models.apisix import APISixConsumer
from app.models.vault import VaultUser
from app.services import apisix, vault
from app.config import (
    VaultInstanceSettings,
    APISixInstanceSettings,
    logger,
)


async def sync_apisix(
    source_apisix: APISixInstanceSettings, target_apisix: APISixInstanceSettings
) -> None:
    """
    Synchronize Apisix consumers from source_apisix to target_apisix. Exit if nothing to sync.

    Args:
        source_apisix (APISixInstanceSettings): Dicitionary representing
        Apisix where consumers are read from.
        target_apisix (APISixInstanceSettings): Dictionary representing
        Apisix where consumers are written to.

    Returns:
        None
    """
    client = AsyncClient()
    source_consumers: list[APISixConsumer | None] = await apisix.get_apisix_consumers(
        client, source_apisix
    )
    logger.debug("Amount of source consumers: '%d'", len(source_consumers))
    logger.debug("Source consumers:\n '%s'", source_consumers)

    if len(source_consumers) == 0 or all(x is None for x in source_consumers):
        logger.info("No consumers to sync in source Apisix '%s'", source_apisix.admin_url)
        return
    for consumer in source_consumers:
        if not consumer:
            continue
        await apisix.upsert_apisix_consumer(client, target_apisix, consumer)


async def sync_vault(
    source_vault: VaultInstanceSettings, target_vault: VaultInstanceSettings
) -> None:
    """
    Synchronize Vault user from source_vault to target_vault.
    Exit if nothing to sync.

    Args:
        source_vault (VaultInstanceSettings): Dicitionary representing
        Vault where users are read from.
        target_vault (VaultInstanceSettings): Dictionary representing
        Vault where users are written to.

    Returns:
        None
    """
    client = AsyncClient()
    vault_user_ids: list[str | None] = await vault.list_user_identifiers_from_vault(
        client, source_vault
    )

    logger.debug("Vault source_vault user identifiers: \n '%s", vault_user_ids)

    users_to_sync: list[VaultUser | None] = []
    if len(vault_user_ids) == 0 or all(x is None for x in vault_user_ids):
        logger.info("No users to sync in source Vault '%s'", source_vault.url)
        return
    for identifier in vault_user_ids:
        if not identifier:
            continue
        user = await vault.get_user_info_from_vault(client, source_vault, identifier)
        users_to_sync.append(user)

    for user in users_to_sync:
        if user:
            await vault.save_user_to_vault(client, target_vault, user)
        else:
            continue
