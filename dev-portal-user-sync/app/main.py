"""
Validates settings and calls sync functions asynchronously
"""

import asyncio
from app.services import sync
from app.config import (
    ApisixSettings,
    VaultSettings,
    settings,
    logger,
)

from app.exceptions import ParameterError


async def main() -> None:
    """
    Validate settings and gather task to be executed asynchronously
    """

    tasks = []
    apisix_settings: ApisixSettings | None = settings().apisix
    if apisix_settings:
        logger.info(
            "Syncin Apisix from '%s' to '%s'",
            apisix_settings.source_apisix.admin_url,
            apisix_settings.target_apisix.admin_url,
        )
        tasks.append(sync.sync_apisix(apisix_settings.source_apisix, apisix_settings.target_apisix))

    vault_settings: VaultSettings | None = settings().vault
    if vault_settings:
        logger.info(
            "Syncin Vault from '%s' to '%s'",
            vault_settings.source_vault.url,
            vault_settings.target_vault.url,
        )
        tasks.append(sync.sync_vault(vault_settings.source_vault, vault_settings.target_vault))

    else:
        logger.exception("Provide either Vault or Apisix settings")
        raise ParameterError("Parameter error")

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
