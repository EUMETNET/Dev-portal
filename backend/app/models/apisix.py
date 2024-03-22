""""
Apisix models
"""

from typing import Dict, Any, List
from pydantic import BaseModel, field_validator
from app.config import settings

config = settings()


class APISixConsumer(BaseModel):
    """
    Representing an APISIX consumer.

    Attributes:
        username (str): The username of the consumer.
        plugins (Dict[str, Dict[str, Any]]): The plugins associated with the consumer.
    """

    username: str
    plugins: Dict[str, Dict[str, Any]]


class APISixRoutes(BaseModel):
    """
    Represents a list of key auth routes in APISix.

    Attributes:
        routes (List[str]): A list of APISixRoute instances.

    Validators:
        filter_key_auth_routes: Filters out routes that do not have the key-auth plugin enabled.
    """

    routes: List[str]

    @field_validator("routes", mode="before")
    def filter_key_auth_routes(cls, value: List[Dict[str, Any]]) -> List[str]:
        """
        Filters out routes that do not have the key-auth plugin enabled.
        """
        return [
            f"{config.apisix.gateway_url}{route.get('value', {}).get('uri')}"
            for route in value
            if route.get("value", {}).get("plugins", {}).get("key-auth") is not None
        ]
