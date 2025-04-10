"""
Global exceptions for the application
"""


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
