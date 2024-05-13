"""
Access token model
"""

from pydantic import BaseModel, field_validator


class AccessToken(BaseModel):
    """
    Represents a decoded access token provided by a user.

    Attributes:
        sub (str): The subject of the token, the user's ID.
        preferred_username (str): The preferred username of the user.
        realm_access (dict[str, list[str]]):
            A dictionary that maps realm names to a list of access roles.

    Validators:
        validate_admin_role(v: dict[str, list[str]]) -> dict[str, list[str]]:
            Validates that the 'ADMIN' role is present in the 'realm_access' attribute.
    """

    sub: str
    preferred_username: str
    groups: list[str]

    @field_validator("groups")
    def validate_groups(cls, v: list[str]) -> list[str]:
        """
        Validates that user belongs to at least one of 'USER' | 'ADMIN' group(s).
        """
        if not any(group in v for group in ["USER", "ADMIN"]):
            raise ValueError()
        return v
