"""
JWT Token dependency
"""

from jose import jwt, JWTError
from pydantic import BaseModel, validator, ValidationError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import requests
from http import HTTPStatus
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tokenUrl")

config = settings()

class AccessToken(BaseModel):
    """
    Decoded access token provided by user
    """
    preferred_username: str
    realm_access: dict[str, list[str]]

    @validator("realm_access", pre=True)
    def validate_admin_role(cls, v):
        """
        Validate that ADMIN is found from roles
        """
        if "ADMIN" not in v.get("roles"):
            raise ValueError()
        return v


def get_jwk(token: str):
    """
    Retrieve the JSON Web Key (JWK) from a Keycloak server.

    Retrieves the JWK from given server that corresponds to the Key ID (kid) in the JWT header.
    The JWK is used to verify the signature of the JWT.

    Parameters:
    token (str): The JWT as a string.

    Returns:
    dict: The JWK as a dictionary. If no matching JWK is found, an empty dictionary is returned.
    """

    header = jwt.get_unverified_header(token)
    jwks_url = f"{config.keycloak.keycloak_url}/realms/{config.keycloak.realm}/protocol/openid-connect/certs"
    jwks = requests.get(jwks_url).json()
    for key in jwks["keys"]:
        if key["kid"] == header["kid"]:
            return key
    return {}


async def validate_token(token: str = Depends(oauth2_scheme)) -> AccessToken:
    """
    Validate and decode given token
    """
    if not token or token == "undefined":
        print("Token has not been provided")
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token has not been provided")
    try:
        jwk = get_jwk(token)
        payload = jwt.decode(token, jwk, algorithms=["RS256"], audience="account")
        token = AccessToken(**payload)
        return token
    except JWTError as e:
        print("JW Token validation failed: ", e)
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token validation failed")
    except ValidationError:
        print("User does not have valid ADMIN role")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="User does not have valid ADMIN role")
