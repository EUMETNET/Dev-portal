"""
Global exceptions for the application
"""

from typing import cast
from http import HTTPStatus

from app.config import logger


class APISIXError(Exception):
    """
    Custom exception for APISIX errors
    """


class VaultError(Exception):
    """
    Custom exception for Vault errors
    """


class KeycloakError(Exception):
    """
    Custom exception for Keycloak errors
    """


class ParameterError(Exception):
    """
    Custom exception for Parameters errors
    """
