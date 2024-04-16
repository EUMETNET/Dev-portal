"""
Tests for users routes
"""

from typing import Callable, cast
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
from app.services import keycloak
from app.models.keycloak import User

pytestmark = pytest.mark.anyio

config = settings()

BASE_URL = f"http://localhost:{config.server.port}"


async def test_delete_user_without_admin_role_fails(get_keycloak_user_token: Callable) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.delete(
            "/users/123-456-789", headers={"Authorization": f"Bearer {get_keycloak_user_token}"}
        )

        assert response.status_code == 403
        assert response.json() == {"message": "User does not have valid ADMIN role"}


async def test_delete_user_with_admin_role_succeeds(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable
) -> None:
    uuid = await keycloak.create_user(client, User(username="superTester", enabled=True))

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.delete(
            f"/users/{uuid}", headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"}
        )

        assert response.status_code == 200
        assert response.json() == {"message": "OK"}

        assert await keycloak.get_user(client, uuid) is None


async def test_delete_user_and_apikey(
    client: AsyncClient, get_keycloak_realm_admin_token: Callable
) -> None:
    user = User(
        username="superTester",
        enabled=True,
        credentials=[{"type": "password", "value": "superTester", "temporary": False}],
    )
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
            "/getapikey", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert create_api_key_response.status_code == 200

        response = await ac.delete(
            f"/users/{uuid}", headers={"Authorization": f"Bearer {get_keycloak_realm_admin_token}"}
        )

        assert response.status_code == 200
        assert response.json() == {"message": "OK"}
