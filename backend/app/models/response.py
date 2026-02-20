"""
API client response models
"""

from pydantic import BaseModel, Field


class GetAPIKey(BaseModel):
    """
    Response model for the GET /apikey endpoint
    """

    apiKey: str = Field(..., description="The API key for the user")


class MessageResponse(BaseModel):
    """
    Response model for GET /health and DELETE /apikey endpoints

    Can be used also as part of other response models
    """

    message: str = Field(..., description="The response message")


class RouteWithLimits(BaseModel):
    """A route URL with rate limit information"""

    url: str = Field(..., description="The route URL")
    limits: str = Field(..., description="Effective rate limits for the current user")


class GetRoutes(BaseModel):
    """
    Response model for the GET /routes endpoint
    """

    routes: list[RouteWithLimits] = Field(
        ..., description="The routes that require key authentication"
    )
