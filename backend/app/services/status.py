"""
Service for checking the health of external services.
"""

import asyncio
from aiocache import cached, Cache  # type: ignore
from httpx import AsyncClient, HTTPStatusError
from app.config import settings, logger
from app.dependencies.http_client import http_request
from app.models.status import (
    ServiceHealth,
    ServiceStatus,
    StatusResponse,
)

config = settings()

MAX_ATTEMPTS = config.status.max_attempts
RETRY_DELAY = config.status.retry_delay
STATUS_CACHE_TTL = config.status.cache_ttl


async def check_http_service(
    client: AsyncClient,
    name: str,
    url: str,
    max_attempts: int = MAX_ATTEMPTS,
    retry_delay: float = RETRY_DELAY,
) -> ServiceHealth:
    """
    Check a service by performing an HTTP GET request with retry support.

    Attempts the request up to `max_attempts` times before marking the service
    as DOWN. This prevents transient network issues from causing false
    status changes.

    Args:
        client: The HTTP client.
        name: Human-readable service name.
        url: The URL to check.
        max_attempts: Total number of attempts before marking as failed.
        retry_delay: Delay in seconds between retry attempts.

    Returns:
        ServiceHealth with the result.
    """
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            await http_request(client, "GET", url)
            return ServiceHealth(name=name, status=ServiceStatus.UP, url=url)
        except HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code < 500:
                return ServiceHealth(name=name, status=ServiceStatus.DEGRADED, url=url)
            last_error = f"HTTP {status_code}"
        except Exception as e:  # pylint: disable=broad-except
            last_error = str(e)

        if attempt < max_attempts:
            logger.debug("Retry %d/%d for %s: %s", attempt, max_attempts, name, last_error)
            await asyncio.sleep(retry_delay)

    logger.warning(
        "Service check failed for %s after %d attempts: %s", name, max_attempts, last_error
    )
    return ServiceHealth(name=name, status=ServiceStatus.DOWN, url=url)


def determine_overall_status(services: list[ServiceHealth]) -> ServiceStatus:
    """Determine the overall status based on individual service statuses."""
    if not services:
        return ServiceStatus.UP
    statuses = [s.status for s in services]
    if all(s == ServiceStatus.UP for s in statuses):
        return ServiceStatus.UP
    if all(s == ServiceStatus.DOWN for s in statuses):
        return ServiceStatus.DOWN
    return ServiceStatus.DEGRADED


@cached(cache=Cache.MEMORY, ttl=STATUS_CACHE_TTL, key="service_status")
async def fetch_service_status(client: AsyncClient) -> StatusResponse:
    """
    Fetch and cache the status of all configured external services.

    Services are loaded from config. Results are cached in memory for
    STATUS_CACHE_TTL seconds.

    Args:
        client: The HTTP client used for making requests.

    Returns:
        StatusResponse with overall and per-service status.
    """
    logger.debug("Got a request to check service status")

    checks = [check_http_service(client, svc.name, svc.url) for svc in config.status.services]

    if not checks:
        logger.warning("No services configured for status monitoring")

    results = await asyncio.gather(*checks)
    services = results
    overall = determine_overall_status(results)

    logger.debug("Service status check complete: %s", overall.value)
    return StatusResponse(overall=overall, services=services)
