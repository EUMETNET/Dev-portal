"""
Service for interacting with the APISIX API.
"""

from typing import Callable, Coroutine, Any
from functools import lru_cache
from httpx import AsyncClient, HTTPError
from app.config import settings, APISixInstanceSettings, logger
from app.dependencies.http_client import http_request
from app.models.request import User
from app.models.apisix import APISixConsumer, APISixRoutes, APISixConsumerGroup
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
    client: AsyncClient, instance: APISixInstanceSettings, user: User | APISixConsumer
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
        if isinstance(user, APISixConsumer):
            apisix_consumer = user
        else:
            apisix_consumer = APISixConsumer(
                instance_name=instance.name,
                username=user.id,
                plugins={
                    "key-auth": {
                        "key": f"{config.apisix.key_path}{user.id}/{config.apisix.key_name}"
                    }
                },
                group_id=user.groups,
            )
        await http_request(
            client,
            "PUT",
            f"{instance.admin_url}/apisix/admin/consumers",
            headers=create_headers(instance.admin_api_key),
            json=apisix_consumer.model_dump(
                exclude=(
                    {"instance_name", "group_id"}
                    if not apisix_consumer.group_id
                    else {"instance_name"}
                )
            ),  # APISix does not expect the instance_name nor not defined group_id field
        )
        logger.info(
            "Upserted APISIX user '%s' in instance '%s'", apisix_consumer.username, instance.name
        )
        return apisix_consumer
    except HTTPError as e:
        logger.exception(
            "Error upserting APISIX user '%s' to instance '%s'",
            apisix_consumer.username,
            instance.name,
        )
        raise APISIXError("APISIX service error") from e


async def get_apisix_consumer(
    client: AsyncClient, instance: APISixInstanceSettings, identifier: str
) -> APISixConsumer | None:
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
            f"{instance.admin_url}/apisix/admin/consumers/{identifier}",
            headers=create_headers(instance.admin_api_key),
            valid_status_codes=(200, 404),
        )
        # response = make_request("GET", f"consumers/{username}", accepted_status_codes=[200, 404])
        # {'key': '/apisix/consumers/foobar',
        #'value': {'create_time': 1710165806, 'plugins':
        # {'key-auth': {'key': '$secret://vault/dev/foobar/key-auth'}},
        # 'username': 'foobar', 'update_time': 1710232230}}
        data = response.json()
        return (
            APISixConsumer(instance_name=instance.name, **data["value"])
            if response.status_code in {200, 201}
            else None
        )
    except HTTPError as e:
        logger.exception(
            "Error retrieving APISIX user '%s' from instance '%s'", identifier, instance.name
        )
        raise APISIXError("APISIX service error") from e


async def get_apisix_consumer_group(
    client: AsyncClient, instance: APISixInstanceSettings, group_id: str
) -> APISixConsumerGroup | None:
    """
    Retrieve a consumer group from given APISIX instance.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        instance (APISixInstanceSettings): The APISIX instance configuration.
        group_id (str): The consumer group ID.

    Returns:
        dict[str, Any] | None: The consumer group data if found, None otherwise.

    Raises:
        APISIXError: If there is an HTTP error while retrieving the consumer group.
    """
    try:
        response = await http_request(
            client,
            "GET",
            f"{instance.admin_url}/apisix/admin/consumer_groups/{group_id}",
            headers=create_headers(instance.admin_api_key),
            valid_status_codes=(200, 404),
        )
        # response = make_request(
        #     "GET", f"consumer_groups/{group_id}", accepted_status_codes=[200, 404]
        # )
        # {
        #   'key': '/apisix/consumer_groups/foobar',
        #   'value': {
        #       'create_time': 1771223965,
        #       'plugins': {
        #           'limit-count': {
        #               'key': 'consumer_name',
        #               'count': 100,
        #               'time_window': 60,
        #               'rejected_code': 503
        #           }
        #       },
        #       'id': 'foobar',
        #       'update_time': 1771310683
        #   }
        # }
        data = response.json()
        return (
            APISixConsumerGroup(instance_name=instance.name, **data["value"])
            if response.status_code in {200, 201}
            else None
        )
    except HTTPError as e:
        logger.exception(
            "Error retrieving APISIX consumer group '%s' from instance '%s'",
            group_id,
            instance.name,
        )
        raise APISIXError("APISIX service error") from e


async def get_routes(client: AsyncClient, instance: APISixInstanceSettings) -> APISixRoutes:
    """
    Retrieve a list of key-auth routes from APISIX.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.

    Returns:
        list[str]: A list of routes.

    Raises:
        APISIXError: If there is an HTTP error while retrieving the routes.
    """
    try:
        response = await http_request(
            client,
            "GET",
            f"{instance.admin_url}/apisix/admin/routes",
            headers=create_headers(instance.admin_api_key),
        )
        routes = response.json().get("list", [])
        # {'total': 1,
        #'list': [{'value':
        # {'update_time': 1710230570, 'plugins':
        # {'key-auth': {'hide_credentials': False, 'query': 'apikey', 'header': 'apikey'},
        #'proxy-rewrite': {'use_real_request_uri_unsafe': False, 'uri': '/'}},
        #'priority': 0, 'uri': '/foo', 'create_time': 1710225526, 'upstream':
        # {'type': 'roundrobin', 'pass_host': 'pass', 'nodes': {'httpbin.org:80': 1},
        #'hash_on': 'vars', 'scheme': 'http'}, 'status': 1, 'id': 'foo'},
        #'createdIndex': 101, 'key': '/apisix/routes/foo', 'modifiedIndex': 128}]}
        return APISixRoutes(gateway_url=config.apisix.global_gateway_url, routes=routes)
    except HTTPError as e:
        logger.exception("Error retrieving APISIX routes from instance '%s'", instance.name)
        raise APISIXError("APISIX service error") from e


async def delete_apisix_consumer(
    client: AsyncClient, instance: APISixInstanceSettings, user: User
) -> APISixConsumer:
    """
    Delete a consumer from APISIX.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the consumer.

    Returns:
        APISixConsumer: An object representing the APISIX consumer

    Raises:
        APISIXError: If there is an HTTP error while deleting the consumer.
    """
    try:
        await http_request(
            client,
            "DELETE",
            f"{instance.admin_url}/apisix/admin/consumers/{user.id}",
            headers=create_headers(instance.admin_api_key),
        )
        logger.info("Deleted APISIX user '%s' from instance '%s'", user.id, instance.name)
        return APISixConsumer(
            instance_name=instance.name,
            username=user.id,
            plugins={
                "key-auth": {"key": f"{config.apisix.key_path}{user.id}/{config.apisix.key_name}"}
            },
            group_id=user.groups,
        )
    except HTTPError as e:
        logger.exception(
            "Error deleting APISIX user '%s' from instance '%s'", user.id, instance.name
        )
        raise APISIXError("APISIX service error") from e


def apisix_instances_missing_user(users: list[APISixConsumer | None]) -> list[str]:
    """
    Find the APISIX instances where the user is missing.

    Args:
        users (list[APISixConsumer | None]): The users to check for.

    Returns:
        list(str): A list of instance names where the user is missing.
    """
    return [
        instance.name
        for instance, user in zip(config.apisix.instances, users)
        if user is None or instance.name != user.instance_name
    ]


def create_tasks(
    func: Callable[..., Coroutine], client: AsyncClient, *args: Any, **kwargs: Any
) -> list[Coroutine]:
    """
    Create tasks to execute a function multiple times.

    Args:
        func (Callable[..., Awaitable]): The function to execute.

    Returns:
        List[Coroutine]: A list of coroutines,
            each of which is a call to `func` for an APISix instance.
            If 'instances' is provided in kwargs, tasks are created only for those instances.
            If 'instances' is not provided, tasks are created for all APISix instances.
    """
    consumers: dict[str, APISixConsumer] = kwargs.pop("consumers", {})
    instances: list[str] | None = kwargs.pop("instances", None)

    if consumers:
        return [
            func(client, instance, consumers[instance.name], *args, **kwargs)
            for instance in config.apisix.instances
            if instance.name in consumers
        ]
    return [
        func(client, instance, *args, **kwargs)
        for instance in config.apisix.instances
        if instances is None or instance.name in instances
    ]


def determine_rate_limits(
    route_plugins: dict[str, Any],
    consumer: APISixConsumer | None,
    consumer_group: APISixConsumerGroup | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str]:
    """
    Determine the effective rate limits based on APISIX precedence hierarchy.

    Args:
        route_plugins (dict[str, Any]): Plugins configured on the route.
        consumer (APISixConsumer | None): The consumer object.
        consumer_group (APISixConsumerGroup | None): The consumer group configuration.

    Returns:
        tuple[dict[str, Any] | None, dict[str, Any] | None, str]: A tuple containing
            (limit_req, limit_count, source) where source indicates which level
            the limits came from.
    """
    # Check consumer first (highest precedence)
    if consumer and consumer.plugins:
        consumer_limit_req = consumer.plugins.get("limit-req")
        consumer_limit_count = consumer.plugins.get("limit-count")

        # If consumer has ANY rate limit plugin, use only consumer-level plugins
        if consumer_limit_req or consumer_limit_count:
            return consumer_limit_req, consumer_limit_count, "consumer"

    # Check consumer group next (medium precedence)
    if consumer_group and consumer_group.plugins:
        group_plugins = consumer_group.plugins
        group_limit_req = group_plugins.get("limit-req")
        group_limit_count = group_plugins.get("limit-count")

        # If consumer group has ANY rate limit plugin, use only group-level plugins
        if group_limit_req or group_limit_count:
            return group_limit_req, group_limit_count, "Group limit"

    # Fall back to route-level (lowest precedence)
    if route_plugins:
        route_limit_req = route_plugins.get("limit-req")
        route_limit_count = route_plugins.get("limit-count")

        return route_limit_req, route_limit_count, "Route limit"

    return None, None, "none"


async def get_routes_with_limits(
    client: AsyncClient,
    instance: APISixInstanceSettings,
    consumer: APISixConsumer | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve routes with their effective rate limits for a consumer.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        instance (APISixInstanceSettings): The APISIX instance configuration.
        consumer (APISixConsumer | None): The consumer to check limits for.

    Returns:
        list[dict[str, Any]]: A list of routes with rate limit information.

    Raises:
        APISIXError: If there is an HTTP error while retrieving the routes.
    """
    try:
        # Get consumer group if consumer exists
        consumer_group = None
        if consumer and consumer.group_id:
            consumer_group = await get_apisix_consumer_group(client, instance, consumer.group_id)

        # Get raw route data for limit checking
        response = await http_request(
            client,
            "GET",
            f"{instance.admin_url}/apisix/admin/routes",
            headers=create_headers(instance.admin_api_key),
        )
        raw_routes = response.json().get("list", [])

        routes_with_limits = []
        for route in raw_routes:
            plugins = route.get("value", {}).get("plugins", {})
            uri = route.get("value", {}).get("uri")

            # Only process routes with key-auth
            if plugins.get("key-auth") is None:
                continue

            # Determine effective rate limits
            limit_req, limit_count, source = determine_rate_limits(
                plugins, consumer, consumer_group
            )

            # Format limits as a human-readable string
            limits_str = format_rate_limits(limit_req, limit_count, source)

            routes_with_limits.append(
                {
                    "url": f"{config.apisix.global_gateway_url}{uri}",
                    "limits": limits_str,
                }
            )

        return routes_with_limits

    except HTTPError as e:
        logger.exception("Error retrieving routes with limits from instance '%s'", instance.name)
        raise APISIXError("APISIX service error") from e

def format_time_window(seconds: int) -> str:
    if seconds % 86400 == 0:
        days = seconds // 86400
        return f"{days}d"
    elif seconds % 3600 == 0:
        hours = seconds // 3600
        return f"{hours}h"
    elif seconds % 60 == 0:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        return f"{seconds}s"

def format_rate_limits(
    limit_req: dict[str, Any] | None, limit_count: dict[str, Any] | None, source: str
) -> str:
    """
    Format rate limit information into a human-readable string.

    Args:
        limit_req (dict[str, Any] | None): The limit-req configuration.
        limit_count (dict[str, Any] | None): The limit-count configuration.
        source (str): The source of the limits.

    Returns:
        str: A formatted string describing the rate limits.
    """
    if not limit_req and not limit_count:
        return "No rate limits"

    parts = []

    # Add quota limit (limit-count)
    if limit_count:
        count = limit_count.get("count")
        time_window = limit_count.get("time_window")
        if count and time_window:
            window_str = format_time_window(time_window)
            parts.append(f"Quota: {count} req/{window_str}")

    # Add request rate limit (limit-req)
    if limit_req:
        rate = limit_req.get("rate")
        burst = limit_req.get("burst")

        if rate:
            parts.append(f"Rate: {rate} req/s")
        if burst:
            parts.append(f"Burst: {burst} req")

    limits_str = " | ".join(parts) if parts else "No rate limits"

    return f"{limits_str} ({source})"
