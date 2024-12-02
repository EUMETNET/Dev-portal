"""
Service for interacting with the APISIX API.
"""

from typing import Callable, Coroutine, Any
from functools import lru_cache
from httpx import AsyncClient, HTTPError
from app.config import settings, APISixInstanceSettings, logger
from app.dependencies.http_client import http_request
from app.models.request import User
from app.models.apisix import APISixConsumer, APISixRoutes
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
        return APISixRoutes(gateway_url=instance.gateway_url, routes=routes)
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
