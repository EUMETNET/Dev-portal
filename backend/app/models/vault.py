""""
Vault models
"""

from pydantic import BaseModel
from app.config import settings

config = settings()

if config.apisix.key_name != "auth_key":
    raise ValueError(
        "Configuration mismatch: Key name used in APISix does not match the one used in Vault"
    )


class VaultUser(BaseModel):
    """
    Representing an Vault user.

    Attributes:
        auth_key (str): The key name used for api key.
        date (str): The date user was created.
    """

    # The key name for 'auth_key' field must match with value of
    # app.config.settings.VAULT_API_KEY_FIELD_NAME
    id: str
    auth_key: str
    date: str
    instance_name: str
