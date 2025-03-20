from typing import Callable
import pytest
from httpx import AsyncClient
from app.config import settings
from app.services.apisix import (
    upsert_apisix_consumer,
    get_apisix_consumer,
    get_routes,
    delete_apisix_consumer,
)
from app.exceptions import APISIXError
from app.models.request import User

config = settings()

# This is the same as using the @pytest.mark.anyio on all test functions in the module
pytestmark = pytest.mark.anyio


async def test_api6_user_not_found(client: AsyncClient) -> None:
    apisix_instance = config.apisix.instances[0]
    identifier = "testuser"
    response = await get_apisix_consumer(client, apisix_instance, identifier)
    assert response is None


async def test_create_and_delete_api6_consumer_success(client: AsyncClient) -> None:
    apisix_instance = config.apisix.instances[0]
    user = User(id="supermario", groups=["USER"])
    response = await upsert_apisix_consumer(client, apisix_instance, user)
    assert response.username == user.id

    await delete_apisix_consumer(client, apisix_instance, user)


async def test_delete_api6_user_not_found_should_raise_error(client: AsyncClient) -> None:
    apisix_instance = config.apisix.instances[0]
    user = User(id="testuser", groups=["USER"])
    with pytest.raises(APISIXError):
        await delete_apisix_consumer(client, apisix_instance, user)


async def test_get_api6_routes(client: AsyncClient) -> None:
    # Routes are created in conftest.py in setup_apisix()
    # Current implementation does not list routes that does not have key-auth plugin defined
    apisix_instance = config.apisix.instances[0]
    response = await get_routes(client, apisix_instance)
    assert len(response.routes) == 2
    assert f"{apisix_instance.gateway_url}/foo" in response.routes
    assert f"{apisix_instance.gateway_url}/bar" in response.routes
