"""
Service for interacting with the APISIX API.
"""

from functools import lru_cache
from httpx import AsyncClient, HTTPError
from app.config import settings, APISixInstanceSettings, logger
from app.dependencies.http_client import http_request
from app.models.request import User
from app.models.apisix import APISixConsumer
from app.exceptions import APISIXError

config = settings()


@lru_cache
def create_headers(api_key: str) -> dict[str, str]:
    """
    Create headers for an HTTP request to APISix.

    This function is decorated with `lru_cache` meaning
    headers for a given API key are only created once and then cached for future use.

    Args:
        api_key (str): The API key to include in the headers.

    Returns:
        dict[str, str]: A dictionary containing the headers.
            The dictionary includes the 'Content-Type' set to 'application/json'
            and the 'X-API-KEY' set to the provided API key.
    """
    return {"Content-Type": "application/json", "X-API-KEY": api_key}


async def upsert_apisix_consumer(
    client: AsyncClient, instance: APISixInstanceSettings, apisix_consumer: APISixConsumer
) -> APISixConsumer:
    """
    Upsert a consumer in APISIX.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the consumer.

    Returns:
        APISixConsumer: A Pydantic model representing the created consumer.

    Raises:
        APISIXError: If there is an HTTP error while creating the consumer.
    """
    try:
        # This block happens when attempting to rollback the apisix consumer
        await http_request(
            client,
            "PUT",
            f"{instance.admin_url}/apisix/admin/consumers",
            headers=create_headers(instance.admin_api_key),
            json=apisix_consumer.model_dump(
                exclude=({"group_id"} if not apisix_consumer.group_id else set())
            ),  # APISix does not expect not defined group_id field
        )
        logger.info(
            "Upserted APISIX user '%s' in instance '%s'",
            apisix_consumer.username,
            instance.admin_url,
        )
        return apisix_consumer
    except HTTPError as e:
        logger.exception(
            "Error upserting APISIX user '%s' to instance '%s'",
            apisix_consumer.username,
            instance.admin_url,
        )
        raise APISIXError("APISIX service error") from e


async def get_apisix_consumers(
    client: AsyncClient, instance: APISixInstanceSettings
) -> list[APISixConsumer | None]:
    """
    Retrieve a consumer for identity from given APISIX instance.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the consumer.

    Returns:
        APISixConsumer: A dictionary representing the consumer if found, None otherwise.

    Raises:
        APISIXError: If there is an HTTP error while retrieving the consumer.
    """
    try:
        response = await http_request(
            client,
            "GET",
            f"{instance.admin_url}/apisix/admin/consumers/",
            headers=create_headers(instance.admin_api_key),
            valid_status_codes=(200, 404),
        )
        data = response.json()
        if response.status_code in {200, 201}:
            return [APISixConsumer(**x["value"]) for x in data["list"]]
        else:
            return [None]
    except HTTPError as e:
        logger.exception("Error retrieving APISIX user from instance '%s'", instance.admin_url)
        raise APISIXError("APISIX service error") from e
