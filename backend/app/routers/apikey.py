from functools import wraps
from typing import Any
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from hvac.exceptions import VaultError
from httpx import AsyncClient
from app.config import settings
from app.dependencies.jwt_token import validate_token, AccessToken
from app.dependencies.http_client import get_http_client
from app.services.vault import get_user_info_from_vault, save_user_to_vault
from app.services.apisix import create_apisix_consumer, check_if_user_exists, get_routes

router = APIRouter()

config = settings()


def handle_exceptions(func):
    """
    Handle all the exceptions that are not caught by the route
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print("Uncaught error: ", e)
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail="General service error",
            )

    return wrapper


# For now just refactor the existing endpoint as is
# Either naming this route differently or creating routes for routes and user
@router.get("/getapikey")
@handle_exceptions
async def get_api_key(
    token: AccessToken = Depends(validate_token),
    client: AsyncClient = Depends(get_http_client),
):
    username = token.preferred_username
    try:
        vault_user = get_user_info_from_vault(username)
        apisix_user = await check_if_user_exists(username)
    except VaultError as e:
        print("Error connecting to vault service, error: ", e)
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="Vault service error")
    except HTTPException as e:
        print("Error communicating with APISix, error: ", e)
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="APISix service error")

    api_key = vault_user.get(config.apisix.key_name)

    if not vault_user:
        print("User not found in vault --> Saving user to vault")
        try:
            api_key = save_user_to_vault(username)
        except VaultError as e:
            print("Error saving user to Vault: ", e)
            raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE, detail="Vault service error")

    if not apisix_user:
        print("User not found in apisix --> Creating user to apisix")
        try:
            await create_apisix_consumer(username)
        except HTTPException as e:
            print("Error saving user to APISIX: ", e)
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                detail="APISix service error",
            )

    print("retrieving all the routes that requires key authentication")
    routes = await get_routes()
    return JSONResponse(status_code=200, content={"apiKey": api_key, "routes": routes})
