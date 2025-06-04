from typing import Callable
import pytest
from httpx import AsyncClient
from app.config import settings
from app.services.apisix import (
    delete_apisix_consumer,
    upsert_apisix_consumer,
    get_apisix_consumers
)
from app.exceptions import APISIXError
from app.models.request import User
from app.models.apisix import APISixConsumer

config = settings()

# This is the same as using the @pytest.mark.anyio on all test functions in the module
pytestmark = pytest.mark.anyio


async def test_api6_user_not_found(client: AsyncClient) -> None:
    apisix_instance = config.apisix.source_apisix
    response = await get_apisix_consumers(client, apisix_instance)
    assert response is list[None]


async def test_create_and_delete_api6_consumer_success(client: AsyncClient) -> None:
    apisix_instance = config.apisix.target_apisix
    consumer = APISixConsumer(username="supermario",plugins={"key-auth": { "key": "secret"}}, group_id="USER")
    response = await upsert_apisix_consumer(client, apisix_instance, consumer)
    assert response.username == consumer.username

    await delete_apisix_consumer(client, apisix_instance, consumer)


async def test_delete_api6_user_not_found_should_raise_error(client: AsyncClient) -> None:
    apisix_instance = config.source_apisix
    consumer = APISixConsumer(username="testuser",plugins={"key-auth": { "key": "secret"}}, group_id="USER")
    with pytest.raises(APISIXError):
        await delete_apisix_consumer(client, apisix_instance, consumer)
