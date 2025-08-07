from datetime import datetime, timezone
import pytest
from freezegun import freeze_time
from httpx import AsyncClient
from app.services import vault
from app.config import settings
from app.models.vault import VaultUser

config = settings()

# This is the same as using the @pytest.mark.anyio on all test functions in the module
pytestmark = pytest.mark.anyio


async def test_vault_user_not_found_wont_raise_exception(client: AsyncClient) -> None:
    # Vault returns 404 if user is not found which is not error in this context
    instance = config.vault.source_vault
    identifier = "testuser"
    response = await vault.get_user_info_from_vault(client, instance, identifier)
    assert response is None


@freeze_time("2021-01-01 00:00:00")
async def test_vault_user_creation_success(client: AsyncClient) -> None:
    identifier = "supermario"
    apikey = "123"
    instance = config.vault.target_vault

    user = VaultUser(id=identifier, auth_key=apikey, date="2021/01/01 00:00:00")

    await vault.save_user_to_vault(client, instance, user)
    response = await vault.get_user_info_from_vault(client, instance, identifier)

    assert response is not None
    assert response == user
