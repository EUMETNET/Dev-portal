"""
Vault models
"""

from pydantic import BaseModel
from app.config import settings

config = settings()


class VaultUser(BaseModel):
    """
    Representing an Vault user.

    Attributes:
        auth_key (str): The key name used for api key.
        date (str): The date user was created.
    """

    id: str
    auth_key: str
    date: str
