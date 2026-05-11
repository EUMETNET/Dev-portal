"""
Status service tests
"""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient, Response, Request
from httpx import HTTPStatusError
from app.services.status import check_http_service, determine_overall_status
from app.models.status import ServiceHealth, ServiceStatus

# This is the same as using the @pytest.mark.anyio on all test functions in the module
pytestmark = pytest.mark.anyio


def test_determine_overall_status_all_up() -> None:
    services = [
        ServiceHealth(name="A-Service", status=ServiceStatus.UP, url="https://a-example.com"),
        ServiceHealth(name="B-Service", status=ServiceStatus.UP, url="https://b-example.com"),
    ]
    assert determine_overall_status(services) == ServiceStatus.UP


def test_determine_overall_status_all_down() -> None:
    services = [
        ServiceHealth(name="A-Service", status=ServiceStatus.DOWN, url="https://a-example.com"),
        ServiceHealth(name="B-Service", status=ServiceStatus.DOWN, url="https://b-example.com"),
    ]
    assert determine_overall_status(services) == ServiceStatus.DOWN


def test_determine_overall_status_mixed_is_degraded() -> None:
    services = [
        ServiceHealth(name="A-Service", status=ServiceStatus.UP, url="https://a-example.com"),
        ServiceHealth(name="B-Service", status=ServiceStatus.DOWN, url="https://b-example.com"),
    ]
    assert determine_overall_status(services) == ServiceStatus.DEGRADED


def test_determine_overall_status_empty_list_is_up() -> None:
    assert determine_overall_status([]) == ServiceStatus.UP


async def test_check_http_service_returns_up_on_success() -> None:
    with patch("app.services.status.http_request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = Response(200)
        result = await check_http_service(
            AsyncClient(), "Test", "https://example.com", max_attempts=1, retry_delay=0
        )

    assert result.status == ServiceStatus.UP
    assert result.name == "Test"
    assert result.url == "https://example.com"


async def test_check_http_service_returns_degraded_on_4xx() -> None:
    mock_response = Response(403, request=Request("GET", "https://example.com"))
    with patch(
        "app.services.status.http_request",
        new_callable=AsyncMock,
        side_effect=HTTPStatusError("Forbidden", request=mock_response.request, response=mock_response),
    ):
        result = await check_http_service(
            AsyncClient(), "Test", "https://example.com", max_attempts=1, retry_delay=0
        )

    assert result.status == ServiceStatus.DEGRADED


async def test_check_http_service_returns_down_on_5xx() -> None:
    mock_response = Response(503, request=Request("GET", "https://example.com"))
    with patch(
        "app.services.status.http_request",
        new_callable=AsyncMock,
        side_effect=HTTPStatusError("Unavailable", request=mock_response.request, response=mock_response),
    ):
        result = await check_http_service(
            AsyncClient(), "Test", "https://example.com", max_attempts=1, retry_delay=0
        )

    assert result.status == ServiceStatus.DOWN


async def test_check_http_service_returns_down_on_connection_error() -> None:
    with patch(
        "app.services.status.http_request",
        new_callable=AsyncMock,
        side_effect=Exception("Connection refused"),
    ):
        result = await check_http_service(
            AsyncClient(), "Test", "https://example.com", max_attempts=1, retry_delay=0
        )

    assert result.status == ServiceStatus.DOWN


async def test_check_http_service_retries_before_marking_down() -> None:
    with patch(
        "app.services.status.http_request",
        new_callable=AsyncMock,
        side_effect=Exception("Connection refused"),
    ) as mock_request:
        result = await check_http_service(
            AsyncClient(), "Test", "https://example.com", max_attempts=3, retry_delay=0
        )

    assert result.status == ServiceStatus.DOWN
    assert mock_request.call_count == 3


async def test_check_http_service_succeeds_on_retry() -> None:
    with patch(
        "app.services.status.http_request",
        new_callable=AsyncMock,
        side_effect=[Exception("Connection refused"), Response(200)],
    ) as mock_request:
        result = await check_http_service(
            AsyncClient(), "Test", "https://example.com", max_attempts=3, retry_delay=0
        )

    assert result.status == ServiceStatus.UP
    assert mock_request.call_count == 2