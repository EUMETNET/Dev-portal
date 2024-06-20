"""
API key business logic related tests
"""

import pytest
from pytest import MonkeyPatch
from httpx import AsyncClient
from app.config import settings
from app.services import vault, apisix, apikey
from app.exceptions import APISIXError, VaultError
from app.models.request import User


async def test_getting_vault_user_fails_raises_error(
    client: AsyncClient, monkeypatch: MonkeyPatch
) -> None:
    """
    Test that an error is raised when getting a user from Vault fails.
    """
    mock_uuid = "mockuuid"
    settings_instance = settings()
    monkeypatch.setattr(settings_instance.vault, "url", "http://mock.vault.url")

    with pytest.raises(VaultError):
        await apikey.get_user_from_vault_and_apisixes(client, mock_uuid)


async def test_getting_apisix_users_fails_raises_error(
    client: AsyncClient, monkeypatch: MonkeyPatch
) -> None:
    """
    Test that an error is raised when getting a user from one APISIX instance fails.
    """
    mock_uuid = "mockuuid"
    settings_instance = settings()
    monkeypatch.setattr(settings_instance.apisix.instances[0], "admin_api_key", "notvalidkey")

    with pytest.raises(APISIXError):
        await apikey.get_user_from_vault_and_apisixes(client, mock_uuid)


async def test_handling_rollback_from_create_succeeds(client: AsyncClient) -> None:
    """
    Test that the rollback from creation is successful and doesn't raise an error.
    """

    user = User(id="mockuuid", groups=["USER"])
    apisix_instance = settings().apisix.instances[0]

    vault_user = await vault.save_user_to_vault(client, user.id)
    apisix_user_1 = await apisix.create_apisix_consumer(client, apisix_instance, user)

    mock_apisix_create_responses = [apisix_user_1, APISIXError()]
    apisix_instances = [instance.name for instance in settings().apisix.instances]

    await apikey.handle_rollback(client, user, vault_user, mock_apisix_create_responses, "CREATE")

    assert None == await vault.get_user_info_from_vault(client, user.id)

    assert None == await apisix.get_apisix_consumer(client, apisix_instance, user.id)


async def test_handling_rollback_from_delete_succeeds(client: AsyncClient) -> None:
    """
    Test that the rollback from deletion is successful and doesn't raise an error.
    """
    user = User(id="mockuuid", groups=["USER"])
    apisix_instance = settings().apisix.instances[0]

    vault_user = await vault.save_user_to_vault(client, user.id)
    apisix_user_1 = await apisix.create_apisix_consumer(client, apisix_instance, user)

    await vault.delete_user_from_vault(client, user.id)
    delete_response = await apisix.delete_apisix_consumer(client, apisix_instance, user)

    mock_apisix_delete_responses = [delete_response, APISIXError()]
    apisix_instances = [instance.name for instance in settings().apisix.instances]

    await apikey.handle_rollback(client, user, vault_user, mock_apisix_delete_responses, "DELETE")

    assert vault_user == await vault.get_user_info_from_vault(client, user.id)

    assert apisix_user_1 == await apisix.get_apisix_consumer(client, apisix_instance, user.id)

    # Check that the user was not recreated back in the second APISIX instance
    # Since user was not there in a first place
    assert None == await apisix.get_apisix_consumer(client, settings().apisix.instances[1], user.id)


async def test_handling_rollback_fails_with_vault(
    client: AsyncClient, monkeypatch: MonkeyPatch
) -> None:
    """
    Test that failing rollback with Vault raises error.
    """

    user = User(id="mockuuid", groups=["USER"])
    apisix_instance = settings().apisix.instances[0]

    vault_user = await vault.save_user_to_vault(client, user.id)
    apisix_user_1 = await apisix.create_apisix_consumer(client, apisix_instance, user)

    mock_apisix_create_responses = [apisix_user_1, APISIXError()]

    settings_instance = settings()
    vault_url = settings_instance.vault.url
    monkeypatch.setattr(settings_instance.vault, "url", "http://mock.vault.url")

    with pytest.raises(VaultError):
        await apikey.handle_rollback(
            client, user, vault_user, mock_apisix_create_responses, "CREATE"
        )

    monkeypatch.setattr(settings_instance.vault, "url", vault_url)

    assert vault_user == await vault.get_user_info_from_vault(client, user.id)

    assert None == await apisix.get_apisix_consumer(client, apisix_instance, user.id)
