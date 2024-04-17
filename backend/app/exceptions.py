"""
Global exceptions for the application
"""

from typing import cast
from http import HTTPStatus
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import logger


class APISIXError(Exception):
    """
    Custom exception for APISIX errors
    """


class VaultError(Exception):
    """
    Custom exception for Vault errors
    """


class KeycloakError(Exception):
    """
    Custom exception for Keycloak errors
    """


async def http_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """
    Handle raised HTTP exceptions
    """
    # The param type is actually HTTPException, but to make everyone happy we use Exception
    # and cast (ugly) it to HTTPException
    # Param type should be changed back to HTTPException once the issue below is fixed
    # https://github.com/encode/starlette/pull/2403
    exc = cast(HTTPException, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)},
    )


async def general_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """
    Handle other exceptions that might happen during the processing of a request
    """
    logger.exception("An unexpected error occurred: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        content={"message": "An unexpected error occurred."},
    )
