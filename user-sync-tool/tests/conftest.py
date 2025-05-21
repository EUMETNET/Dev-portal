"""
Pytest fixtures for actual tests.
"""

from typing import AsyncGenerator
import asyncio
import pytest
from httpx import AsyncClient
from app.config import settings, APISixInstanceSettings
from tests.data import apisix

config = settings()


def get_apisix_headers(instance: APISixInstanceSettings) -> dict[str, str]:
    """ """
    return {"Content-Type": "application/json", "X-API-KEY": instance.admin_api_key}



@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    """
    Pytest fixture that sets the backend for AnyIO to 'asyncio' for the entire test session.

    This fixture is automatically used (due to `autouse=True`) for all tests in the session.
    It ensures that AnyIO, a library for asynchronous I/O, uses the 'asyncio' library as its backend

    Returns:
        str: The name of the AnyIO backend to use.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Yield an instance of httpx client for tests.
    """
    async with AsyncClient() as c:
        yield c


# ------- VAULT SETUP ---------
@pytest.fixture(scope="session", autouse=True)
async def vault_setup(client: AsyncClient) -> AsyncGenerator[None, None]:
    """
    Setup vault for tests.
    """

    # Remove all the secrets
    instances = [config.vault.source_vault, config.vault.target_vault]
    secret_responses = await asyncio.gather(
        *[
            client.get(
                f"{instance.url}/v1/{instance.base_path}/?list=true",
                headers={"X-Vault-Token": instance.token},
            )
            for instance in instances
        ]
    )

    await asyncio.gather(
        *[
            client.delete(
                f"{instance.url}/v1/{instance.base_path}/{secret}",
                headers={"X-Vault-Token": instance.token},
            )
            for instance, response in zip(instances, secret_responses)
            for secret in response.json()["data"]["keys"]
        ]
    )


# ------- APISIX SETUP ---------
@pytest.fixture(scope="session", autouse=True)
async def apisix_setup(client: AsyncClient) -> AsyncGenerator[None, None]:
    """
    Setup apisix for tests.
    """
    consumers = apisix.CONSUMERS

    instances = [config.apisix.source_apisix, config.apisix.target_apisix]
    consumers = await asyncio.gather(
        *[
            client.get(
                f"{instance.admin_url}/apisix/admin/consumers", headers=get_apisix_headers(instance)
            )
            for instance in instances
        ]
    )

    await asyncio.gather(
        *[
            client.delete(
                f"{instance.admin_url}/apisix/admin/consumers/{consumer['value']['username']}",
                headers=get_apisix_headers(instance),
            )
            for instance, instance_consumers in zip(instances, consumers)
            for consumer in instance_consumers.json()["list"]
        ]
    )

