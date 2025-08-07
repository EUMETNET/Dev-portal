""""
Apisix models
"""

from typing import Any, Optional
from pydantic import BaseModel
from app.constants import USER_GROUP


class APISixConsumer(BaseModel):
    """
    Representing an APISIX consumer.

    Attributes:
        username (str): The username of the consumer.
        plugins (dict[str, dict[str, Any]]): The plugins associated with the consumer.
        group_id (Optional[str]): The group ID of the consumer group.
    """

    username: str
    plugins: dict[str, dict[str, Any]]
    group_id: Optional[str] = USER_GROUP


class APISixConsumerGroup(BaseModel):
    """
    Representing an APISIX consumer.

    Attributes:
        username (str): The username of the consumer.
        plugins (dict[str, dict[str, Any]]): The plugins associated with the consumer.
        group_id (Optional[str]): The group ID of the consumer group.
    """

    id: str
    plugins: dict[str, dict[str, Any]]
