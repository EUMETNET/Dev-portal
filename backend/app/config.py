"""
Application configurations
"""

import os
from typing import Type
from functools import lru_cache
import logging
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from app.constants import VAULT_API_KEY_FIELD_NAME


class APISixInstanceSettings(BaseSettings):
    """
    APISix instance settings model
    """

    name: str
    admin_url: str
    gateway_url: str
    admin_api_key: str


class APISixSettings(BaseSettings):
    """
    APISix settings model
    """

    key_path: str
    key_name: str = VAULT_API_KEY_FIELD_NAME
    instances: list[APISixInstanceSettings]


class VaultInstanceSettings(BaseSettings):
    """
    Vault instance settings model
    """

    name: str
    url: str
    token: str


class VaultSettings(BaseSettings):
    """
    Vault settings model
    """

    base_path: str
    secret_phase: str
    instances: list[VaultInstanceSettings]


class KeyCloakSettings(BaseSettings):
    """
    Keycloak settings model
    """

    url: str
    realm: str
    client_id: str
    client_secret: str


class ServerSettings(BaseSettings):
    """
    FastAPI server settings model
    """

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8082)
    log_level: str = Field(default="INFO")
    allowed_origins: list[str] = Field(default=["*"])


# Link to docs where this is explained
# https://docs.pydantic.dev/latest/concepts/pydantic_settings/#other-settings-source
class Settings(BaseSettings):
    """
    Application settings model
    """

    server: ServerSettings
    apisix: APISixSettings
    vault: VaultSettings
    keycloak: KeyCloakSettings

    # Look first for specific config file or config.yaml
    # and fall back to the default config.default.yaml
    model_config = SettingsConfigDict(
        yaml_file=[
            "config.default.yaml",
            "secrets.default.yaml",
            os.getenv("CONFIG_FILE", "config.yaml"),
            os.getenv("SECRETS_FILE", "secrets.yaml"),
        ]
    )

    # pylint: disable=too-many-positional-arguments,too-many-arguments
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


@lru_cache
def settings() -> Settings:
    """
    Load and cache the settings from given yaml config file.

    Returns:
        Settings: The loaded and cached settings.

    """
    return Settings()


# Set the log level
logger = logging.getLogger("uvicorn")
log_level = getattr(logging, settings().server.log_level.upper(), logging.INFO)
logger.setLevel(log_level)
