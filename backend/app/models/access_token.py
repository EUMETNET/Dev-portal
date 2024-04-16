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
    realm_access: dict[str, list[str]]

    @field_validator("realm_access")
    def validate_roles(cls, v: dict[str, list[str]]) -> dict[str, list[str]]:
        """
        Validates that user has at least one of 'USER' | 'ADMIN' role(s).
        """
        user_roles = v.get("roles", [])
        if not any(role in user_roles for role in ("USER", "ADMIN")):
            raise ValueError()
        return v
