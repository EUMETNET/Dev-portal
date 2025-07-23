"""
Pytest fixtures for actual tests.
"""

from typing import AsyncGenerator
import asyncio
import pytest
from httpx import AsyncClient
from app.config import settings, APISixInstanceSettings
from tests.data import apisix, keycloak

config = settings()


def get_apisix_headers(instance: APISixInstanceSettings) -> dict[str, str]:
    """ """
    return {"Content-Type": "application/json", "X-API-KEY": instance.admin_api_key}


async def get_realm_group_id_by_name(client: AsyncClient, group_name: str) -> str:
    """
    Get the group ID of a realm group by its name.

    Args:
        name (str): The name of the realm group.

    Returns:
        str: The group ID of the realm group.
    """
    url = f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/groups"

    admin_access_token = await get_keycloak_admin_token(client)

    auth_header = {
        "Authorization": f"Bearer {admin_access_token}",
    }
    groups = await client.get(url=url, headers=auth_header)

    # with open("tests/data/realm-export.json", encoding="utf-8") as f:
    #    realm_json = json.load(f)

    for group in groups.json():
        if group["name"] == group_name:
            return group["id"]
    raise ValueError(f'Group "{group_name}" not found in the realm export data.')


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

    yield

    # Remove all the secrets
    secret_responses = await asyncio.gather(
        *[
            client.get(
                f"{instance.url}/v1/{config.vault.base_path}/?list=true",
                headers={"X-Vault-Token": instance.token},
            )
            for instance in config.vault.instances
        ]
    )

    await asyncio.gather(
        *[
            client.delete(
                f"{instance.url}/v1/{config.vault.base_path}/{secret}",
                headers={"X-Vault-Token": instance.token},
            )
            for instance, response in zip(config.vault.instances, secret_responses)
            for secret in response.json()["data"]["keys"]
        ]
    )


# ------- APISIX SETUP ---------
@pytest.fixture(scope="session", autouse=True)
async def apisix_setup(client: AsyncClient) -> AsyncGenerator[None, None]:
    """
    Setup apisix for tests.
    """
    # Add some test routes
    routes = apisix.ROUTES

    routes_requests = [
        client.put(
            f"{instance.admin_url}/apisix/admin/routes",
            json=route,
            headers=get_apisix_headers(instance),
        )
        for route in routes
        for instance in config.apisix.instances
    ]

    await asyncio.gather(
        *routes_requests,
    )

    yield

    # Clean up created resources
    await asyncio.gather(
        *[
            client.delete(
                f"{instance.admin_url}/apisix/admin/routes/{route['id']}",
                headers=get_apisix_headers(instance),
            )
            for instance in config.apisix.instances
            for route in routes
        ],
    )

    consumers = await asyncio.gather(
        *[
            client.get(
                f"{instance.admin_url}/apisix/admin/consumers", headers=get_apisix_headers(instance)
            )
            for instance in config.apisix.instances
        ]
    )

    await asyncio.gather(
        *[
            client.delete(
                f"{instance.admin_url}/apisix/admin/consumers/{consumer['value']['username']}",
                headers=get_apisix_headers(instance),
            )
            for instance, instance_consumers in zip(config.apisix.instances, consumers)
            for consumer in instance_consumers.json()["list"]
        ]
    )


# ------- KEYCLOAK SETUP ---------
async def get_keycloak_admin_token(client: AsyncClient) -> str:
    """
    Pytest fixture that retrieves a admin user access token from Keycloak.

    This fixture makes a POST request to the Keycloak token endpoint
    with the client ID, username, and password.
    It then extracts the access token from the response and returns it.

    The access token can be used in other fixtures or tests
    to authenticate requests to APIs that use Keycloak for authentication.

    Returns:
        str: The access token for the user.
    """
    token_url = f"{config.keycloak.url}/realms/master/protocol/openid-connect/token"
    data = keycloak.KEYCLOAK_ADMIN_USER_TOKEN_DATA
    response = await client.post(token_url, data=data)
    access_token = response.json()["access_token"]
    assert isinstance(access_token, str), "access_token is not a string"
    return access_token


@pytest.fixture(scope="session", autouse=True)
async def keycloak_setup(client: AsyncClient) -> AsyncGenerator[None, None]:
    """
    Setup keycloak for tests.
    """
    # Setup keycloak
    admin_access_token = await get_keycloak_admin_token(client)

    auth_header = {
        "Authorization": f"Bearer {admin_access_token}",
    }

    users = keycloak.KEYCLOAK_USERS

    user_url = f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/users"

    await asyncio.gather(
        *[
            client.post(user_url, json=user, headers=auth_header)
            for user in users
            if "skip_init_creation" not in user
        ]
    )

    yield

    # Get test user's id and delete it
    admin_access_token = await get_keycloak_admin_token(client)

    kc_users = await client.get(user_url, headers=auth_header)

    await asyncio.gather(
        *[
            client.delete(
                f"{user_url}/{user['id']}",
                headers={"Authorization": f"Bearer {admin_access_token}"},
            )
            for user in kc_users.json()
        ]
    )


@pytest.fixture
async def get_keycloak_user_token(client: AsyncClient) -> str:
    """
    Pytest fixture that retrieves a user access token from Keycloak.

    This fixture makes a POST request to the Keycloak token endpoint
    with the client ID, username, and password.
    It then extracts the access token from the response and returns it.

    The access token can be used in other fixtures or tests
    to authenticate requests to APIs that use Keycloak for authentication.

    Returns:
        str: The access token for the user.
    """
    token_url = (
        f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/token"
    )
    data = {
        "client_id": "frontend",
        "username": keycloak.KEYCLOAK_USERS[0]["username"],
        "password": keycloak.KEYCLOAK_USERS[0]["credentials"][0]["value"],
        "grant_type": "password",
    }
    response = await client.post(token_url, data=data)
    access_token = response.json()["access_token"]
    assert isinstance(access_token, str), "access_token is not a string"
    return access_token


@pytest.fixture
async def get_keycloak_user_2_token_no_groups(client: AsyncClient) -> str:
    """
    Pytest fixture that retrieves a user access token from Keycloak.

    This fixture makes a POST request to the Keycloak token endpoint
    with the client ID, username, and password.
    It then extracts the access token from the response and returns it.

    The access token can be used in other fixtures or tests
    to authenticate requests to APIs that use Keycloak for authentication.

    Returns:
        str: The access token for the user.
    """

    await remove_keycloak_user_from_group(client)
    token_url = (
        f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/token"
    )
    data = {
        "client_id": "frontend",
        "username": keycloak.KEYCLOAK_USERS[1]["username"],
        "password": keycloak.KEYCLOAK_USERS[1]["credentials"][0]["value"],
        "grant_type": "password",
    }
    response = await client.post(token_url, data=data)
    access_token = response.json()["access_token"]
    assert isinstance(access_token, str), "access_token is not a string"
    return access_token


@pytest.fixture
async def get_keycloak_realm_admin_token(client: AsyncClient) -> str:
    """
    Pytest fixture that retrieves a admin user's access token from Keycloak.

    Adds user to the realm group "Admin" before retrieving the token.

    The access token can be used in other fixtures or tests
    to authenticate requests to APIs that use Keycloak for authentication.

    Returns:
        str: The access token for the admin user.
    """

    await add_keycloak_user_to_group(client)

    token_url = (
        f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/token"
    )
    data = {
        "client_id": "frontend",
        "username": keycloak.KEYCLOAK_USERS[2]["username"],
        "password": keycloak.KEYCLOAK_USERS[2]["credentials"][0]["value"],
        "grant_type": "password",
    }
    response = await client.post(token_url, data=data)
    access_token = response.json()["access_token"]
    assert isinstance(access_token, str), "access_token is not a string"
    return access_token


async def remove_keycloak_user_from_group(client: AsyncClient) -> None:
    """
    Asynchronously removes a Keycloak user from a group.

    This function first retrieves an admin access token from Keycloak,
    then uses that token to authenticate a GET request to the Keycloak users endpoint.
    It extracts the user ID from the response, then sends a DELETE request
    to the user's groups endpoint to remove the user from the group.

    The group to be removed from is defined within the function and is currently hardcoded.

    Note: This function assumes that the Keycloak server, realm,
    and user are all configured correctly.
    """
    admin_access_token = await get_keycloak_admin_token(client)

    auth_header = {
        "Authorization": f"Bearer {admin_access_token}",
    }

    user = keycloak.KEYCLOAK_USERS[1]

    user_url = f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/users"

    r = await client.get(f"{user_url}?username={user['username']}", headers=auth_header)

    user_id = r.json()[0]["id"]

    # Define the group ID to remove the user from
    group_id = await get_realm_group_id_by_name(client, "User")

    # Remove the user from the group
    group_url = (
        f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/users"
        f"/{user_id}/groups/{group_id}"
    )

    await client.request("DELETE", group_url, headers=auth_header)


async def add_keycloak_user_to_group(client: AsyncClient) -> None:
    """
    Asynchronously adds a Keycloak user to a group.

    This function first retrieves an admin access token from Keycloak,
    then uses that token to authenticate a GET request to the Keycloak users endpoint.
    It extracts the user ID from the response, then sends a PUT request
    to the user's groups endpoint to add the user to the group.

    The group to be added to is defined within the function and is currently hardcoded.

    Note: This function assumes that the Keycloak server, realm,
    and user are all configured correctly.
    """
    admin_access_token = await get_keycloak_admin_token(client)

    auth_header = {
        "Authorization": f"Bearer {admin_access_token}",
    }

    user = keycloak.KEYCLOAK_USERS[2]

    user_url = f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/users"

    r = await client.get(f"{user_url}?username={user['username']}", headers=auth_header)

    user_id = r.json()[0]["id"]

    # Define the group ID to add the user to
    group_id = await get_realm_group_id_by_name(client, "Admin")

    # Add the user to the group
    group_url = (
        f"{config.keycloak.url}/admin/realms/{config.keycloak.realm}/users"
        f"/{user_id}/groups/{group_id}"
    )

    await client.request("PUT", group_url, headers=auth_header)
