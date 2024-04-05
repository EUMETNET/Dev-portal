"""
Tests for health routes
"""

from typing import Callable, cast
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings

pytestmark = pytest.mark.anyio

config = settings()

BASE_URL = f"http://localhost:{config.server.port}"


async def test_get_health_success() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data == {"message": "OK"}


async def test_get_health_fails_with_vault(monkeypatch) -> None:
    settings_instance = settings()
    monkeypatch.setattr(settings_instance.vault, "url", "http://mock.vault.url")

    async with AsyncClient(
        transport=ASGITransport(app=cast(Callable, app)), base_url=BASE_URL
    ) as ac:
        response = await ac.get("/health")

    assert response.status_code == 503
    data = response.json()

    assert data == {"message": "Vault service error"}
