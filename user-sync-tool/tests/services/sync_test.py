import pytest
from httpx import AsyncClient
from app.config import settings
from app.services.apisix import delete_apisix_consumer, upsert_apisix_consumer, get_apisix_consumers
from app.services.vault import save_user_to_vault, get_user_info_from_vault
from app.exceptions import APISIXError
from app.models.apisix import APISixConsumer
from app.models.vault import VaultUser
from app.constants import USER_GROUP
from app.main import main

config = settings()

# This is the same as using the @pytest.mark.anyio on all test functions in the module
pytestmark = pytest.mark.anyio


async def test_syncing_user_to_apisix(client: AsyncClient) -> None:
    apisix_instance = config.apisix.source_apisix
    consumer = APISixConsumer(username="supermario", plugins={"key-auth": {"key": "secret"}})
    response = await upsert_apisix_consumer(client, apisix_instance, consumer)
    assert response.username == consumer.username

    await main()

    consumers = await get_apisix_consumers(client, config.apisix.target_apisix)

    assert len(consumers) == 1
    assert consumers[0].username == consumer.username


async def test_syncing_user_to_vault(client: AsyncClient) -> None:
    identifier = "supermario"
    apikey = "123"
    instance = config.vault.source_vault
    date = "2021/01/01 00:00:00"

    user = VaultUser(id=identifier, auth_key=apikey, date=date)

    await save_user_to_vault(client, instance, user)

    await main()

    response = await get_user_info_from_vault(client, config.vault.target_vault, identifier)

    assert response.id == identifier
    assert response.auth_key == apikey
    assert response.date == date


async def test_syncing_both_apisix_and_vault(client: AsyncClient) -> None:
    identifier = "supermario"
    apikey = "123"
    instance = config.vault.source_vault
    date = "2021/01/01 00:00:00"

    user = VaultUser(id=identifier, auth_key=apikey, date=date)

    await save_user_to_vault(client, instance, user)

    consumer = APISixConsumer(username=identifier, plugins={"key-auth": {"key": apikey}})

    await upsert_apisix_consumer(client, config.apisix.source_apisix, consumer)

    await main()

    response = await get_user_info_from_vault(client, config.vault.target_vault, identifier)
    assert response.id == identifier
    assert response.auth_key == apikey
    assert response.date == date

    consumers = await get_apisix_consumers(client, config.apisix.target_apisix)
    assert len(consumers) == 1
    assert consumers[0].username == identifier
    assert (
        consumers[0].group_id == USER_GROUP
    )  # Each consumer should belong to the default user group if not specified
