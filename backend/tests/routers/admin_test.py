"""
Tests for users routes
"""

from typing import Callable, cast
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
from app.services import keycloak, apikey, apisix
from app.models.keycloak import User as KeycloakUser
from app.models.request import User
from app.exceptions import KeycloakError
from tests.data.keycloak import KEYCLOAK_USERS

pytestmark = pytest.mark.anyio

config = settings()

BASE_URL = f"http://localhost:{config.server.port}"


async def test_delete_user_without_admin_role_fails(get_keycloak_user_token: Callable) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.delete(
            "/admin/users/123-456-789",
            headers={"Authorization": f"Bearer {get_keycloak_user_token}"},
        )

        assert response.status_code == 403
        assert response.json() == {"message": "User does not belong to ADMIN group"}


async def test_delete_user_with_admin_role_succeeds(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable
) -> None:
    uuid = await keycloak.create_user(client, KeycloakUser(**KEYCLOAK_USERS[3]))

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.delete(
            f"/admin/users/{uuid}",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "OK"}

        assert await keycloak.get_user(client, uuid) is None


async def test_delete_user_and_apikey(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable
) -> None:
    user = KeycloakUser(**KEYCLOAK_USERS[3])

    uuid = await keycloak.create_user(client, user)

    token_url = (
        f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/token"
    )
    data = {
        "client_id": "frontend",
        "username": user.username,
        "password": user.credentials[0]["value"],
        "grant_type": "password",
    }
    response = await client.post(token_url, data=data)
    access_token = response.json()["access_token"]

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        create_api_key_response = await ac.get(
            "/apikey", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert create_api_key_response.status_code == 200

        response = await ac.delete(
            f"/admin/users/{uuid}",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "OK"}

        assert await keycloak.get_user(client, uuid) is None


async def test_delete_user_exception_rolls_user_api_key_back(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable, monkeypatch
) -> None:
    async def mock_delete_user(client: AsyncClient, user_uuid: str) -> None:
        raise KeycloakError()

    user = KeycloakUser(**KEYCLOAK_USERS[3])
    uuid = await keycloak.create_user(client, user)

    req_user = User(id=uuid, groups=["USER"])

    og_delete_user_func = keycloak.delete_user

    token_url = (
        f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/token"
    )
    data = {
        "client_id": "frontend",
        "username": user.username,
        "password": user.credentials[0]["value"],
        "grant_type": "password",
    }
    response = await client.post(token_url, data=data)
    access_token = response.json()["access_token"]

    monkeypatch.setattr("app.services.keycloak.delete_user", mock_delete_user)

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        create_api_key_response = await ac.get(
            "/apikey", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert create_api_key_response.status_code == 200

        response = await ac.delete(
            f"/admin/users/{uuid}",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
        )

        assert response.status_code == 503
        assert response.json() == {"message": "Keycloak service error"}

        vault_users, apisix_consumers = await apikey.get_user_from_vault_and_apisix_instances(
            client, req_user.id
        )

        assert all(user for user in vault_users)

        assert all(user for user in apisix_consumers)

        # Delete keycloak user
        await og_delete_user_func(client, uuid)


async def test_disable_user(client: AsyncClient, get_keycloak_realm_admin_token: Callable) -> None:
    user = KeycloakUser(**KEYCLOAK_USERS[3])
    uuid = await keycloak.create_user(client, user)

    token_url = (
        f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/token"
    )
    data = {
        "client_id": "frontend",
        "username": user.username,
        "password": user.credentials[0]["value"],
        "grant_type": "password",
    }
    response = await client.post(token_url, data=data)
    access_token = response.json()["access_token"]

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        create_api_key_response = await ac.get(
            "/apikey", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert create_api_key_response.status_code == 200

        response = await ac.put(
            f"/admin/users/{uuid}/disable",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "OK"}

        user = await keycloak.get_user(client, uuid)

        assert user.enabled == False

        await keycloak.delete_user(client, uuid)


async def test_enable_user(client: AsyncClient, get_keycloak_realm_admin_token: Callable) -> None:
    user = KeycloakUser(**KEYCLOAK_USERS[3])
    uuid = await keycloak.create_user(client, user)

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        disable_response = await ac.put(
            f"/admin/users/{uuid}/disable",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
        )

        assert disable_response.status_code == 200

        user = await keycloak.get_user(client, uuid)

        assert user.enabled == False

        response = await ac.put(
            f"/admin/users/{uuid}/enable",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "OK"}

        user = await keycloak.get_user(client, uuid)

        assert user.enabled == True

        await keycloak.delete_user(client, uuid)


async def test_add_user_to_eumetnet_user_group(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable
) -> None:
    user = KeycloakUser(**KEYCLOAK_USERS[3])
    uuid = await keycloak.create_user(client, user)

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.put(
            f"/admin/users/{uuid}/update-group",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
            json={"groupName": "EUMETNET_USER"},
        )

        assert response.status_code == 200
        assert response.json() == {"message": "OK"}

        user = await keycloak.get_user(client, uuid)

        assert set(user.groups) == {"EUMETNET_USER", "USER"}

        await keycloak.delete_user(client, uuid)


async def test_add_user_and_existing_apikey_to_eumetnet_user_group(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable
) -> None:
    user = KeycloakUser(**KEYCLOAK_USERS[3])
    uuid = await keycloak.create_user(client, user)

    parsed_user = User(id=uuid, groups=["USER"])

    token_url = (
        f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/token"
    )
    data = {
        "client_id": "frontend",
        "username": user.username,
        "password": user.credentials[0]["value"],
        "grant_type": "password",
    }
    response = await client.post(token_url, data=data)
    access_token = response.json()["access_token"]

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        create_api_key_response = await ac.get(
            "/apikey", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert create_api_key_response.status_code == 200

        update_response = await ac.put(
            f"/admin/users/{uuid}/update-group",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
            json={"groupName": "EUMETNET_USER"},
        )

        assert update_response.status_code == 200
        assert update_response.json() == {"message": "OK"}

        user = await keycloak.get_user(client, uuid)

        _vault_users, apisix_consumers = await apikey.get_user_from_vault_and_apisix_instances(
            client, parsed_user.id
        )

        for consumer in apisix_consumers:
            assert consumer.group_id == "EUMETNET_USER"

        assert set(user.groups) == {"EUMETNET_USER", "USER"}

        await keycloak.delete_user(client, uuid)


async def test_remove_user_from_eumetnet_user_group(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable
) -> None:
    user = KeycloakUser(**KEYCLOAK_USERS[3])
    uuid = await keycloak.create_user(client, user)

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        add_group_response = await ac.put(
            f"/admin/users/{uuid}/update-group",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
            json={"groupName": "EUMETNET_USER"},
        )

        assert add_group_response.status_code == 200
        assert add_group_response.json() == {"message": "OK"}

        user = await keycloak.get_user(client, uuid)

        assert set(user.groups) == {"EUMETNET_USER", "USER"}

        rm_group_response = await ac.put(
            f"/admin/users/{uuid}/remove-group",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
            json={"groupName": "EUMETNET_USER"},
        )

        assert rm_group_response.status_code == 200
        assert rm_group_response.json() == {"message": "OK"}

        user = await keycloak.get_user(client, uuid)

        assert set(user.groups) == {"USER"}

        await keycloak.delete_user(client, uuid)


async def test_remove_user_and_existing_apikey_from_eumetnet_user_group(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable
) -> None:
    user = KeycloakUser(**KEYCLOAK_USERS[3])
    uuid = await keycloak.create_user(client, user)

    parsed_user = User(id=uuid, groups=["USER"])

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:

        update_response = await ac.put(
            f"/admin/users/{uuid}/update-group",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
            json={"groupName": "EUMETNET_USER"},
        )

        assert update_response.status_code == 200
        assert update_response.json() == {"message": "OK"}

        token_url = (
            f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/token"
        )
        data = {
            "client_id": "frontend",
            "username": user.username,
            "password": user.credentials[0]["value"],
            "grant_type": "password",
        }
        response = await client.post(token_url, data=data)
        access_token = response.json()["access_token"]

        create_api_key_response = await ac.get(
            "/apikey", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert create_api_key_response.status_code == 200

        user = await keycloak.get_user(client, uuid)

        _vault_users, apisix_consumers = await apikey.get_user_from_vault_and_apisix_instances(
            client, parsed_user.id
        )

        for consumer in apisix_consumers:
            assert consumer.group_id == "EUMETNET_USER"

        assert set(user.groups) == {"EUMETNET_USER", "USER"}

        rm_group_response = await ac.put(
            f"/admin/users/{uuid}/remove-group",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
            json={"groupName": "EUMETNET_USER"},
        )

        assert rm_group_response.status_code == 200
        assert rm_group_response.json() == {"message": "OK"}

        user = await keycloak.get_user(client, uuid)

        _vault_user, apisix_consumers = await apikey.get_user_from_vault_and_apisix_instances(
            client, parsed_user.id
        )

        for consumer in apisix_consumers:
            assert consumer.group_id == None

        assert set(user.groups) == {"USER"}

        await keycloak.delete_user(client, uuid)


async def test_remove_user_from_other_group_persists_group_in_apisix(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable
) -> None:
    """
    Test that removing a user from a group that is not EUMETNET_USER
    does not remove the user from the group in APISIXes
    """
    user = KeycloakUser(**KEYCLOAK_USERS[3])
    uuid = await keycloak.create_user(client, user)

    parsed_user = User(id=uuid, groups=["USER"])

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:

        # Put user to EUMETNET_USER and ADMIN groups
        await ac.put(
            f"/admin/users/{uuid}/update-group",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
            json={"groupName": "EUMETNET_USER"},
        )

        await ac.put(
            f"/admin/users/{uuid}/update-group",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
            json={"groupName": "ADMIN"},
        )

        # Create API key for user
        token_url = (
            f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/token"
        )
        data = {
            "client_id": "frontend",
            "username": user.username,
            "password": user.credentials[0]["value"],
            "grant_type": "password",
        }
        response = await client.post(token_url, data=data)
        access_token = response.json()["access_token"]

        create_api_key_response = await ac.get(
            "/apikey", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert create_api_key_response.status_code == 200

        user = await keycloak.get_user(client, uuid)

        _vault_user, apisix_consumers = await apikey.get_user_from_vault_and_apisix_instances(
            client, parsed_user.id
        )

        for consumer in apisix_consumers:
            assert consumer.group_id == "EUMETNET_USER"

        assert set(user.groups) == {"ADMIN", "EUMETNET_USER", "USER"}

        # Remove user from ADMIN group
        rm_group_response = await ac.put(
            f"/admin/users/{uuid}/remove-group",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
            json={"groupName": "ADMIN"},
        )

        assert rm_group_response.status_code == 200
        assert rm_group_response.json() == {"message": "OK"}

        user = await keycloak.get_user(client, uuid)

        _vault_users, apisix_consumers = await apikey.get_user_from_vault_and_apisix_instances(
            client, parsed_user.id
        )

        for consumer in apisix_consumers:
            assert consumer.group_id == "EUMETNET_USER"

        assert set(user.groups) == {"EUMETNET_USER", "USER"}

        await ac.delete(
            f"/admin/users/{uuid}",
            headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"},
        )

        user = await keycloak.get_user(client, uuid)

        assert user is None
