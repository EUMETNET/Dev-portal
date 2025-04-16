"""
Tests for 'routes' routes
"""

from typing import Callable, cast
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
from tests.data.apisix import ROUTES

pytestmark = pytest.mark.anyio

config = settings()

BASE_URL = f"http://localhost:{config.server.port}"


async def test_get_routes_success(get_keycloak_user_token: Callable) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.get(
            "/routes", headers={"Authorization": f"Bearer {get_keycloak_user_token}"}
        )

    assert response.status_code == 200
    data = response.json()

    assert len(data["routes"]) == 2

    routes = [
        f"{config.apisix.global_gateway_url}{route['uri']}"
        for instance in config.apisix.instances
        for route in ROUTES
        if "key-auth" in route["plugins"]
    ]

    assert set(routes) == set(data["routes"])


async def test_get_routes_without_token_fails() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.get("/routes")

    assert response.status_code == 401
    data = response.json()

    assert data == {"message": "Not authenticated"}
