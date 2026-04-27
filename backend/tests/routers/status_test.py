"""
Tests for status routes
"""

from typing import Callable, cast
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
from app.models.status import ServiceHealth, ServiceStatus
from app.models.response import StatusResponse

pytestmark = pytest.mark.anyio

config = settings()

BASE_URL = f"http://localhost:{config.server.port}"


async def test_get_status_without_token_fails() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.get("/status")

    assert response.status_code == 401
    data = response.json()

    assert data == {"message": "Not authenticated"}


async def test_get_status_with_valid_token_succeeds(get_keycloak_user_token: Callable) -> None:
    mock_response = StatusResponse(
        overall=ServiceStatus.UP,
        services=[
            ServiceHealth(name="Test Service", status=ServiceStatus.UP, url="https://example.com"),
        ],
    )

    with patch(
        "app.services.status.fetch_service_status",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
        ) as ac:
            response = await ac.get(
                "/status", headers={"Authorization": f"Bearer {get_keycloak_user_token}"}
            )

    assert response.status_code == 200
    data = response.json()

    assert data["overall"] == "up"
    assert len(data["services"]) == 1
    assert data["services"][0]["name"] == "Test Service"
    assert data["services"][0]["status"] == "up"
    assert data["services"][0]["url"] == "https://example.com"


async def test_get_status_with_degraded_services(get_keycloak_user_token: Callable) -> None:
    mock_response = StatusResponse(
        overall=ServiceStatus.DEGRADED,
        services=[
            ServiceHealth(name="Service A", status=ServiceStatus.UP, url="https://a.com"),
            ServiceHealth(name="Service B", status=ServiceStatus.DOWN, url="https://b.com"),
        ],
    )

    with patch(
        "app.services.status.fetch_service_status",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
        ) as ac:
            response = await ac.get(
                "/status", headers={"Authorization": f"Bearer {get_keycloak_user_token}"}
            )

    assert response.status_code == 200
    data = response.json()

    assert data["overall"] == "degraded"
    assert len(data["services"]) == 2


async def test_get_status_with_no_services(get_keycloak_user_token: Callable) -> None:
    mock_response = StatusResponse(
        overall=ServiceStatus.UP,
        services=[],
    )

    with patch(
        "app.services.status.fetch_service_status",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
        ) as ac:
            response = await ac.get(
                "/status", headers={"Authorization": f"Bearer {get_keycloak_user_token}"}
            )

    assert response.status_code == 200
    data = response.json()

    assert data["overall"] == "up"
    assert data["services"] == []