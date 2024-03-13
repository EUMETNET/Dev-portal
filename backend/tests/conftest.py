import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.http_client import get_http_client


@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def token():
    url= ""
    payload = {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "grant_type": "password",
        "username": "test-user",
        "password": "test-password",
        "scope": "openid"
    }
    client = get_http_client()
    response = client.post(url, json=payload)
    return response.json()["access_token"]
