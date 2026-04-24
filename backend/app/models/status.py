"""
Service status models
"""

from enum import Enum
from pydantic import BaseModel, Field


class ServiceStatus(str, Enum):
    """Enum representing the status of a service."""

    UP = "up"
    DEGRADED = "degraded"
    DOWN = "down"


class ServiceHealth(BaseModel):
    """
    Representing the health of a single service.

    Attributes:
        name (str): The name of the service.
        status (ServiceStatus): The status of the service.
        url (str): The URL of the service.
    """

    name: str = Field(..., description="The name of the service")
    status: ServiceStatus = Field(..., description="The health status of the service")
    url: str = Field(..., description="The URL of the service")


class StatusResponse(BaseModel):
    """
    Representing the overall status response.

    Attributes:
        overall (ServiceStatus): The overall status across all services.
        services (list[ServiceHealth]): The health of each individual service.
    """

    overall: ServiceStatus = Field(..., description="The overall status across all services")
    services: list[ServiceHealth] = Field(..., description="The health of each individual service")
