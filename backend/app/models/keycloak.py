""""
Keycloak models
"""

from typing import Optional, Any
from pydantic import BaseModel, field_validator
from app.config import settings

config = settings()


class TokenResponse(BaseModel):
    """
    Represents a token response from the TokenEndpoint.
    Currently only the access_token is needed from the response.

    Attributes:
        access_token (str): The access token generated by the TokenEndpoint.
    """

    access_token: str


class User(BaseModel):
    """
    Represents a user in the Keycloak.
    https://www.keycloak.org/docs-api/22.0.1/rest-api/index.html#UserRepresentation

    Attributes:
        id (Optional[str]): The unique identifier of the user.
        createdTimestamp (Optional[int]): The timestamp when the user was created.
        username (Optional[str]): The username of the user.
        enabled (Optional[bool]): Indicates whether the user is enabled or not.
        totp (Optional[bool]): Indicates whether the user has enabled
            Time-based One-Time Password (TOTP) authentication.
        emailVerified (Optional[bool]): Indicates whether the user's email has been verified.
        firstName (Optional[str]): The first name of the user.
        lastName (Optional[str]): The last name of the user.
        email (Optional[str]): The email address of the user.
        disableableCredentialTypes (Optional[list[str]]):
            The types of credentials that can be disabled for the user.
        requiredActions (Optional[list[str]]): The actions that are required for the user.
        notBefore (Optional[int]):
            The timestamp before which the user is not allowed to authenticate.
        access (Optional[dict]): The access rights of the user.
    """

    id: Optional[str] = None
    createdTimestamp: Optional[int] = None
    username: Optional[str] = None
    enabled: Optional[bool] = None
    totp: Optional[bool] = None
    emailVerified: Optional[bool] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    credentials: Optional[list[dict[str, Any]]] = None
    disableableCredentialTypes: Optional[list[str]] = None
    requiredActions: Optional[list[str]] = None
    notBefore: Optional[int] = None
    access: Optional[dict] = None
    groups: Optional[list[str]] = None

    @field_validator("groups", mode="before")
    @classmethod
    def parse_groups(cls, value: list[dict[str, Any]]) -> list[str] | None:
        """
        Parses the groups from the user.
        """
        print(value)
        if value:
            return [group["name"] for group in value]
        return None
