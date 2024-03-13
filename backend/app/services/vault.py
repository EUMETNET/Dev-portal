import hashlib
from typing import TypedDict, Optional
import hvac
from hvac.exceptions import VaultError, InvalidPath
from datetime import datetime
from app.config import settings

config = settings()

client = hvac.Client(url=config.vault.base_url, token=config.vault.token)


class VaultUser(TypedDict):
    api_key: str
    date: str


def generate_md5_hash_value(user_name: str) -> str:
    formatted_date = datetime.utcnow().strftime("%Y%m%d")

    secret_phase = "geeks"
    print(f"Current Date : {formatted_date}")
    print(f"Login Id : {user_name}")
    print(f"Secret Phase : {secret_phase}")

    md5 = hashlib.md5()
    md5.update((formatted_date + user_name + secret_phase).encode())
    api_key = md5.hexdigest()
    print(f"Generated API key: {api_key}")

    return api_key


def save_user_to_vault(user_name: str) -> str:
    generated_api_key = generate_md5_hash_value(user_name)

    vault_values = {config.apisix.key_name: generated_api_key, "date": get_date()}

    try:
        client.secrets.kv.v1.create_or_update_secret(
            path=user_name, secret=vault_values, mount_point=config.vault.base_path
        )
        return generated_api_key
    except VaultError as e:
        raise VaultError from e


def get_user_info_from_vault(user_name: str) -> Optional[VaultUser]:
    try:
        # response looks e.g. like this
        # {'request_id': '2e1de3e3-6f3b-ccc6-28ae-20bc1b620b4f', 'lease_id': '', 'renewable': False, 'lease_duration': 2764800, 'data': {'as': 'as', 'dfdf': 'dfdf'}, 'wrap_info': None, 'warnings': None, 'auth': None}
        response = client.secrets.kv.v1.read_secret(path=user_name, mount_point=config.vault.base_path)
        return VaultUser(**response["data"])
    except InvalidPath:
        return None
    except VaultError as e:
        raise VaultError from e


def get_date():
    return datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
