"""
Service for interacting with the APISIX API.
"""

from typing import Awaitable, Callable, Coroutine, Any
from functools import lru_cache
import asyncio
from httpx import AsyncClient
from app.config import settings, APISixInstanceSettings
from app.dependencies.http_client import http_request
from app.models.apisix import APISixConsumer, APISixRoutes

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


async def create_apisix_consumer(
    client: AsyncClient, instance: APISixInstanceSettings, identifier: str
) -> APISixConsumer:
    """
    Create a consumer in APISIX.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the consumer.

    Returns:
        APISixConsumer: A Pydantic model representing the created consumer.
    """
    apisix_consumer = APISixConsumer(
        instance_name=instance.name,
        username=identifier,
        plugins={
            "key-auth": {"key": f"{config.apisix.key_path}{identifier}/{config.apisix.key_name}"}
        },
    )
    await http_request(
        client,
        "PUT",
        f"{instance.admin_url}/apisix/admin/consumers",
        headers=create_headers(instance.admin_api_key),
        data=apisix_consumer.model_dump(
            exclude={"instance_name"}
        ),  # APISix does not expect the instance_name field
    )
    return apisix_consumer


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
    """
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


async def get_routes(client: AsyncClient, instance: APISixInstanceSettings) -> APISixRoutes:
    """
    Retrieve a list of key-auth routes from APISIX.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.

    Returns:
        list[str]: A list of routes.
    """
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


async def delete_apisix_consumer(
    client: AsyncClient, instance: APISixInstanceSettings, identifier: str
) -> None:
    """
    Delete a consumer from APISIX.

    Args:
        client (AsyncClient): The HTTP client to use for making the request.
        identifier (str): The identifier for the consumer.
    """
    await http_request(
        client,
        "DELETE",
        f"{instance.admin_url}/apisix/admin/consumers/{identifier}",
        headers=create_headers(instance.admin_api_key),
    )


def apisix_instances_missing_user(users: list[APISixConsumer | None]) -> set[str]:
    """
    Find the APISIX instances where the user is missing.

    Args:
        user (APISixConsumer): The user to check for.

    Returns:
        set(str): A set of instance names where the user is missing.
    """
    all_instance_names = set(instance.name for instance in config.apisix.instances)
    instances_with_user = set(user.instance_name for user in users if user is not None)
    return all_instance_names - instances_with_user


def create_tasks(
    func: Callable[..., Coroutine], client: AsyncClient, *args: Any, **kwargs: Any
) -> list[Awaitable]:
    """
    Create tasks to execute a function multiple times.

    Args:
        func (Callable[..., Awaitable]): The function to execute.

    Returns:
        List[Awaitable]: A list of tasks, each of which is a call to `func` for an APISix instance.
            If 'instances' is provided in kwargs, tasks are created only for those instances.
            If 'instances' is not provided, tasks are created for all APISix instances.
    """
    instances = kwargs.pop("instances", set())
    return [
        asyncio.create_task(func(client, instance, *args, **kwargs))
        for instance in config.apisix.instances
        if not instances or instance.name in instances
    ]
