"""
Access token model
"""

from pydantic import BaseModel, field_validator

GROUPS = ["USER", "EUMETNET_USER", "ADMIN"]


class AccessToken(BaseModel):
    """
    Represents a decoded access token provided by a user.

    Attributes:
        sub (str): The subject of the token, the user's ID.
        preferred_username (str): The preferred username of the user.
        groups list[str]: A list of groups the user belongs to.

    Validators:
        validate_groups(v: list[str]) -> list[str]:
            Validates that the user has correct group(s) present in the 'groups' attribute.
    """

    sub: str
    preferred_username: str
    groups: list[str]

    @field_validator("groups")
    def validate_groups(cls, v: list[str]) -> list[str]:
        """
        Validates that user belongs to at least one of 'USER' | 'ADMIN' group(s).
        """
        if not any(group in v for group in GROUPS):
            raise ValueError()
        return v


class User(BaseModel):
    """
    Represents a parsed user.
    """

    id: str
    groups: list[str]

    @field_validator("id")
    @classmethod
    def remove_dashes(cls, value: str) -> str:
        """
        Apisix validation pattern '\"^[a-zA-Z0-9_]+$\"' does not accept dashes in username.
        Removes dashes from the user's uuid.
        """
        return value.replace("-", "")
