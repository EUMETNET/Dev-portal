"""
Access token model
"""

from typing import Dict, List
from pydantic import BaseModel, field_validator


class AccessToken(BaseModel):
    """
    Represents a decoded access token provided by a user.

    Attributes:
        sub (str): The subject of the token, the user's ID.
        preferred_username (str): The preferred username of the user.
        realm_access (Dict[str, List[str]]):
            A dictionary that maps realm names to a list of access roles.

    Validators:
        validate_admin_role(v: Dict[str, List[str]]) -> Dict[str, List[str]]:
            Validates that the 'ADMIN' role is present in the 'realm_access' attribute.
    """

    sub: str
    preferred_username: str
    realm_access: Dict[str, List[str]]

    @field_validator("realm_access")
    def validate_admin_role(cls, v: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Validates that ADMIN is found from roles
        """
        if "ADMIN" not in v.get("roles", []):
            raise ValueError()
        return v
