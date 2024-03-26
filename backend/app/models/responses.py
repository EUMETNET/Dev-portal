"""
API client response models
"""

from pydantic import BaseModel, Field


class GetAPIKey(BaseModel):
    """
    Response model for the GET /apikey endpoint
    """

    apiKey: str = Field(..., description="The API key for the user")
    routes: list[str] = Field(..., description="The routes that require key authentication")


class DeleteAPIKey(BaseModel):
    """
    Response model for the DELETE /apikey endpoint
    """

    message: str = Field(default="OK", description="The message indicating the API key was deleted")
