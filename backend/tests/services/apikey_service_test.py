"""
API key business logic related tests
"""

import pytest
import asyncio
from pytest import MonkeyPatch
from httpx import AsyncClient
from app.config import settings
from app.services import vault, apisix, apikey
from app.exceptions import APISIXError, VaultError
from app.models.request import User
from app.models.vault import VaultUser


async def test_getting_vault_user_fails_raises_error(
    client: AsyncClient, monkeypatch: MonkeyPatch
) -> None:
    """
    Test that an error is raised when getting a user from Vault fails.
    """
    mock_uuid = "mockuuid"
    settings_instance = settings()
    monkeypatch.setattr(settings_instance.vault.instances[0], "url", "http://mock.vault.url")

    with pytest.raises(VaultError):
        await apikey.get_user_from_vault_and_apisix_instances(client, mock_uuid)


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
        await apikey.get_user_from_vault_and_apisix_instances(client, mock_uuid)


async def test_handling_rollback_from_create_succeeds(client: AsyncClient) -> None:
    """
    Test that the rollback from creation is successful and doesn't raise an error.
    """

    user = User(id="mockuuid", groups=["USER"])
    vault_user = VaultUser(
        auth_key=vault.generate_api_key(user.id),
        date=vault.get_formatted_str_date("%Y/%m/%d %H:%M:%S"),
        id=user.id,
        instance_name="",
    )
    apisix_instance = settings().apisix.instances[0]

    vault_responses = await asyncio.gather(
        *vault.create_tasks(vault.save_user_to_vault, client, vault_user)
    )
    apisix_user_1 = await apisix.upsert_apisix_consumer(client, apisix_instance, user)

    print(vault_responses)

    mock_responses = [*vault_responses, apisix_user_1, APISIXError()]

    await apikey.handle_rollback(client, user, mock_responses, "CREATE")

    vault_users = await asyncio.gather(
        *vault.create_tasks(vault.get_user_info_from_vault, client, user.id)
    )

    assert all(vault_user == None for vault_user in vault_users)

    assert None == await apisix.get_apisix_consumer(client, apisix_instance, user.id)


async def test_handling_rollback_from_delete_succeeds(client: AsyncClient) -> None:
    """
    Test that the rollback from deletion is successful and doesn't raise an error.
    """
    user = User(id="mockuuid", groups=["USER"])
    vault_user = VaultUser(
        auth_key=vault.generate_api_key(user.id),
        date=vault.get_formatted_str_date("%Y/%m/%d %H:%M:%S"),
        id=user.id,
        instance_name="",
    )

    apisix_instance = settings().apisix.instances[0]

    await asyncio.gather(*vault.create_tasks(vault.save_user_to_vault, client, vault_user))

    apisix_user_1 = await apisix.upsert_apisix_consumer(client, apisix_instance, user)

    deleted_vault_users = await asyncio.gather(
        *vault.create_tasks(vault.delete_user_from_vault, client, vault_user)
    )
    delete_response = await apisix.delete_apisix_consumer(client, apisix_instance, user)

    mock_delete_responses = [*deleted_vault_users, delete_response, APISIXError()]

    await apikey.handle_rollback(client, user, mock_delete_responses, "DELETE")

    vault_users: list[VaultUser | None] = await asyncio.gather(
        *vault.create_tasks(vault.get_user_info_from_vault, client, user.id)
    )

    for user in vault_users:
        assert user.auth_key == vault_user.auth_key

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
    vault_user = VaultUser(
        auth_key=vault.generate_api_key(user.id),
        date=vault.get_formatted_str_date("%Y/%m/%d %H:%M:%S"),
        id=user.id,
        instance_name="",
    )
    apisix_instance = settings().apisix.instances[0]

    vault_users = await asyncio.gather(
        *vault.create_tasks(vault.save_user_to_vault, client, vault_user)
    )
    apisix_user_1 = await apisix.upsert_apisix_consumer(client, apisix_instance, user)

    mock_create_responses = [*vault_users, apisix_user_1, APISIXError()]

    settings_instance = settings()
    vault_instance_1_url = settings_instance.vault.instances[0].url
    vault_instance_2_url = settings_instance.vault.instances[1].url

    monkeypatch.setattr(settings_instance.vault.instances[0], "url", "http://mock.vault.url")
    monkeypatch.setattr(settings_instance.vault.instances[1], "url", "http://mock.vault.url")

    with pytest.raises(VaultError):
        await apikey.handle_rollback(client, user, mock_create_responses, "CREATE")

    monkeypatch.setattr(settings_instance.vault.instances[0], "url", vault_instance_1_url)
    monkeypatch.setattr(settings_instance.vault.instances[1], "url", vault_instance_2_url)

    vault_users = await asyncio.gather(
        *vault.create_tasks(vault.get_user_info_from_vault, client, vault_user.id)
    )

    assert all(vault_user for vault_user in vault_users)

    assert None == await apisix.get_apisix_consumer(client, apisix_instance, user.id)
