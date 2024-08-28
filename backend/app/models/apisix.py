""""
Apisix models
"""

from typing import Any, Optional
from pydantic import BaseModel, field_validator, ValidationInfo
from app.config import settings
from app.constants import EUMETNET_USER_GROUP

config = settings()


class APISixConsumer(BaseModel):
    """
    Representing an APISIX consumer.

    Attributes:
        instance_name (str): The name of the APISIX instance.
        username (str): The username of the consumer.
        plugins (dict[str, dict[str, Any]]): The plugins associated with the consumer.
        group_id (Optional[str]): The group ID of the consumer group.
    """

    instance_name: str
    username: str
    plugins: dict[str, dict[str, Any]]
    group_id: Optional[str] = None

    @field_validator("group_id", mode="before")
    @classmethod
    def set_group_id(cls, value: list[str]) -> Optional[str]:
        """
        Sets the group_id attribute to 'eumetnet_user' if token has corresponding
        group or default to None.
        """
        if EUMETNET_USER_GROUP in value:
            return EUMETNET_USER_GROUP
        return None


class APISixRoutes(BaseModel):
    """
    Represents a list of key auth routes in APISix.

    Attributes:
        routes (list[str]): A list of APISixRoute instances.

    Validators:
        filter_key_auth_routes: Filters out routes that do not have the key-auth plugin enabled.
    """

    gateway_url: str
    routes: list[str]

    @field_validator("routes", mode="before")
    @classmethod
    def filter_key_auth_routes(cls, value: list[dict[str, Any]], info: ValidationInfo) -> list[str]:
        """
        Filters out routes that do not have the key-auth plugin enabled.
        """
        # info.data dict contains the data passed to the model constructor
        # Note info.data fields are not validated yet because mode="before"
        return [
            f"{info.data['gateway_url']}{route.get('value', {}).get('uri')}"
            for route in value
            if route.get("value", {}).get("plugins", {}).get("key-auth") is not None
        ]
