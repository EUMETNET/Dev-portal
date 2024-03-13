from typing import TypedDict, NotRequired, Any
from fastapi import HTTPException
from httpx import AsyncClient
import requests
import json
from app.config import settings

config = settings()

HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": config.apisix.admin_api_key
}

class APISixConsumer(TypedDict):
    username: str
    plugins: NotRequired[dict[str, dict[str, Any]]]


def create_consumer(username: str) -> APISixConsumer:
    return {
        "username": username,
        "plugins": {
            "key-auth": {
                "key": f"{config.apisix.key_path}{username}/{config.apisix.key_name}"
            }
        }
    }

def make_request(method: str, endpoint: str, data: dict = None, accepted_status_codes: list[int] = None):
    url = f"{config.apisix.admin_api_url}/apisix/admin/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": config.apisix.admin_api_key
    }
    try:
        response = requests.request(method, url, headers=headers, data=json.dumps(data))
        if accepted_status_codes is None or response.status_code not in accepted_status_codes:
            response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException() from e

    return response.json()


async def create_apisix_consumer(client: AsyncClient, username: str):
    response = await client.put(
        f"{config.apisix.admin_api_url}/apisix/admin/consumers",
        headers=HEADERS,
        json=create_consumer(username)
    )

    #response = make_request("PUT", "consumers", create_consumer(username))
    return response.json()


async def check_if_user_exists(client: AsyncClient, username: str):
    response = await client.get(
        f"{config.apisix.admin_api_url}/apisix/admin/consumers/{username}",
        headers=HEADERS,
    )
    #response = make_request("GET", f"consumers/{username}", accepted_status_codes=[200, 404])
    #{'key': '/apisix/consumers/foobar', 'value': {'create_time': 1710165806, 'plugins': {'key-auth': {'key': '$secret://vault/dev/foobar/key-auth'}}, 'username': 'foobar', 'update_time': 1710232230}}
    return response.json().get("value", {}).get("username") == username


async def get_routes(client: AsyncClient):
    response = await client.get(f"{config.apisix.admin_api_url}/apisix/admin/routes", headers=HEADERS)
    #response = make_request("GET", "routes")
    routes = response.json().get("list", [])
    #{'total': 1, 'list': [{'value': {'update_time': 1710230570, 'plugins': {'key-auth': {'hide_credentials': False, 'query': 'apikey', 'header': 'apikey'}, 'proxy-rewrite': {'use_real_request_uri_unsafe': False, 'uri': '/'}}, 'priority': 0, 'uri': '/foo', 'create_time': 1710225526, 'upstream': {'type': 'roundrobin', 'pass_host': 'pass', 'nodes': {'httpbin.org:80': 1}, 'hash_on': 'vars', 'scheme': 'http'}, 'status': 1, 'id': 'foo'}, 'createdIndex': 101, 'key': '/apisix/routes/foo', 'modifiedIndex': 128}]}
    return [
        f"{config.apisix.gateway_url}{route.get('value', {}).get('uri')}" 
        for route in routes 
        if route.get("value", {}).get("plugins", {}).get("key-auth") is not None
    ]
