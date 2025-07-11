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


class APISixInstanceSettings(BaseSettings):
    """
    APISix instance settings model
    """

    admin_url: str
    admin_api_key: str


class ApisixSettings(BaseSettings):
    """
    APISix settings model
    """

    source_apisix: APISixInstanceSettings
    target_apisix: APISixInstanceSettings


class VaultInstanceSettings(BaseSettings):
    """
    Vault instance settings model
    """

    url: str
    token: str
    base_path: str


class VaultSettings(BaseSettings):
    """
    Vault settings model
    """

    source_vault: VaultInstanceSettings
    target_vault: VaultInstanceSettings


# Link to docs where this is explained
# https://docs.pydantic.dev/latest/concepts/pydantic_settings/#other-settings-source
class Settings(BaseSettings):
    """
    Application settings model
    """

    apisix: ApisixSettings | None = None
    vault: VaultSettings | None = None
    log_level: str = Field(default="INFO")

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
logging.basicConfig()
logger = logging.getLogger(__name__)
LOG_LEVEL = getattr(logging, settings().log_level.upper(), logging.INFO)
logger.setLevel(LOG_LEVEL)
