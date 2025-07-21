"""
JWT Token dependency
"""

from http import HTTPStatus
import jwt
from jwt import ExpiredSignatureError, PyJWKClient, PyJWTError
from pydantic import ValidationError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.config import settings, logger
from app.models.request import AccessToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tokenUrl")

config = settings()


async def validate_token(token: str = Depends(oauth2_scheme)) -> AccessToken:
    """
    Validate and decode given token
    """
    if not token or token == "undefined":  # nosec
        logger.exception("Token has not been provided")
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Token has not been provided"
        )
    try:
        jwks_url = (
            f"{config.keycloak.url}/realms/{config.keycloak.realm}" "/protocol/openid-connect/certs"
        )
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(token, signing_key.key, algorithms=["RS256"], audience="account")
        return AccessToken(**payload)
    except ExpiredSignatureError as e:
        logger.exception("JWT Token has expired: %s", e)
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Token signature has expired"
        ) from e
    except PyJWTError as e:
        logger.exception("JW Token validation failed with error: %s", e)
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Token validation failed"
        ) from e
    except ValidationError as e:
        logger.exception(
            "User does not belong to valid group(s). Valid groups are 'User' and/or 'Admin'"
        )
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="User does not belong to valid group(s)"
        ) from e


async def validate_admin_role(
    token: AccessToken = Depends(validate_token),
) -> AccessToken:
    """
    Validate that the user belongs to Admin group
    """
    if "Admin" not in token.groups:
        logger.exception("User '%s' does not have valid Admin group", token.sub)
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="User does not belong to Admin group"
        )
    return token
