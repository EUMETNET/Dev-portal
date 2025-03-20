""""
Apisix models
"""

from typing import Any, Optional
from pydantic import BaseModel, field_validator, ValidationInfo


class APISixConsumer(BaseModel):
    """
    Representing an APISIX consumer.

    Attributes:
        instance_name (str): The name of the APISIX instance.
        username (str): The username of the consumer.
        plugins (dict[str, dict[str, Any]]): The plugins associated with the consumer.
        group_id (Optional[str]): The group ID of the consumer group.
    """

    username: str
    plugins: dict[str, dict[str, Any]]
    group_id: Optional[str] = None
