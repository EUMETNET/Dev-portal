"""
Application configurations
"""

import os
from typing import Type, Tuple
from functools import lru_cache
import logging
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


VAULT_API_KEY_FIELD_NAME = "auth_key"


class APISixSettings(BaseSettings):
    """
    APISix settings model
    """

    admin_api_url: str
    gateway_url: str
    admin_api_key: str
    key_path: str
    key_name: str = VAULT_API_KEY_FIELD_NAME


class VaultSettings(BaseSettings):
    """
    Vault settings model
    """

    base_url: str
    base_path: str
    token: str
    secret_phase: str


class KeyCloakSettings(BaseSettings):
    """
    Keycloak settings model
    """

    keycloak_url: str
    realm: str


# Link to docs where this is explained
# https://docs.pydantic.dev/latest/concepts/pydantic_settings/#other-settings-source
class Settings(BaseSettings):
    """
    Application settings model
    """

    port: int = Field(default=8082)
    log_level: str = Field(default="INFO")
    apisix: APISixSettings
    vault: VaultSettings
    keycloak: KeyCloakSettings

    # Look first for specific config file and fall back to the default config.yaml
    model_config = SettingsConfigDict(yaml_file=os.getenv("CONFIG_YAML", "config.yaml"))

    # pylint: disable=too-many-arguments
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


@lru_cache
def settings() -> Settings:
    """
    Load and cache the settings from a .env file.
    """
    return Settings()


# Set the log level
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.getLevelName(settings().log_level))
