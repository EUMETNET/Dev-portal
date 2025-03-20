import asyncio

from httpx import AsyncClient
from app.models.apisix import APISixConsumer
from app.models.vault import VaultUser
from app.services import apisix, vault
from app.config import settings, APISixInstanceSettings, logger

from app.dependencies import http_client
from app.exceptions import ParameterError


async def sync_apisix() -> None:

    source_apisix: APISixInstanceSettings = settings().apisix.source_apisix
    target_apisix: APISixInstanceSettings = settings().apisix.target_apisix
    client = AsyncClient()
    source_consumers: list[APISixConsumer | None] = await apisix.get_apisix_consumers(
        client, source_apisix
    )
    logger.debug("Amount of source consumers: '%d'", len(source_consumers))
    logger.debug("Source consumers:\n '%s'", source_consumers)

    if len(source_consumers) > 0:
        client = AsyncClient()
        for consumer in source_consumers:
            if not (consumer):
                pass
            else:
                await apisix.upsert_apisix_consumer(client, target_apisix, consumer)


async def sync_vault() -> None:
    source = settings().vault.source_vault
    target = settings().vault.target_vault
    client = AsyncClient()
    vault_user_ids: list[str | None] = await vault.list_user_identifiers_from_vault(client, source)

    if not vault_user_ids:
        return

    logger.debug("Vault source user identifiers: \n '%s", vault_user_ids)
    users_to_sync: list[VaultUser | None] = [await vault.get_user_info_from_vault(client, source, id) for id in vault_user_ids]

    for user in users_to_sync:
        await vault.save_user_to_vault(client, target, user)

def main():

    if settings().apisix:
        logger.info(
            "Syncin Apisix from '%s' to '%s'",
            settings().apisix.source_apisix.admin_url,
            settings().apisix.target_apisix.admin_url,
        )
        asyncio.run(sync_apisix())

    if settings().vault:
        logger.info(
            "Syncin Vault from '%s' to '%s'",
            settings().vault.source_vault.url,
            settings().vault.target_vault.url,
        )
        asyncio.run(sync_vault())

    else:
        logger.exception("Provide both source and target Apisix settings")
        raise ParameterError("Parameter error")


if __name__ == "__main__":
    main()
