from functools import lru_cache
from pydantic import BaseSettings


class APISixSettings(BaseSettings):
    admin_api_url: str
    gateway_url: str
    admin_api_key: str
    key_path: str
    key_name: str


class VaultSettings(BaseSettings):
    base_url: str
    base_path: str
    token: str


class KeyCloakSettings(BaseSettings):
    keycloak_url: str
    realm: str


class Settings(BaseSettings):
    apisix: APISixSettings
    vault: VaultSettings
    keycloak: KeyCloakSettings

    def __init__(self, *args, **kwargs):
        kwargs["apisix"] = APISixSettings(_env_file=kwargs["_env_file"])
        kwargs["vault"] = VaultSettings(_env_file=kwargs["_env_file"])
        kwargs["keycloak"] = KeyCloakSettings(_env_file=kwargs["_env_file"])
        super().__init__(*args, **kwargs)


# Cache the settings loading
@lru_cache
def settings() -> Settings:
    return Settings(_env_file=".env")
