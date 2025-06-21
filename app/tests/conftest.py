import os
import pytest
from typing import Generator
from starlette.testclient import TestClient
import jwt

from app.utils.jwt_utils import JWTUtils, JWTException

os.environ["TESTING"] = "True"

from app.core.config import settings
from app.main import app

access_token = ""


@pytest.fixture(scope='module')
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope='module')
def get_invitation_code(client: TestClient) -> str:
    """Test generating an invitation code"""
    response = client.post(
        url=f"{settings.BASE_URL}/invitation-code/generate-invitation-code",
        headers={"Content-Type": "application/json",
                 "api-key": settings.ADMIN_API_KEY},
    )
    assert response.status_code == 200
    result = response.json()
    # Verify that the invitation_code field exists
    assert "invitation_code" in result
    return result["invitation_code"]


# Test checking the invitation code
@pytest.fixture(scope='module')
def get_access_token(client: TestClient, get_invitation_code) -> str:
    if access_token is not None and access_token != "":
        return access_token
    """Test checking the invitation code"""
    response = client.post(
        url=f"{settings.BASE_URL}/auth/check-invitation-code",
        headers={"Content-Type": "application/json"},
        json={"invitation_code": get_invitation_code},
    )
    assert response.status_code == 200
    result = response.json()
    # Verify that the access_token field exists
    assert "access_token" in result
    return result["access_token"]

def test_decode_token_expired(monkeypatch):
    jwt_utils = JWTUtils()
    expired_token = jwt.encode({'exp': 0}, jwt_utils.secret_key, algorithm=jwt_utils.algorithm)
    with pytest.raises(JWTException, match="Token expired"):
        jwt_utils.decode_token(expired_token)

def test_decode_token_invalid():
    jwt_utils = JWTUtils()
    invalid_token = "invalid.token.string"
    with pytest.raises(JWTException, match="Invalid token"):
        jwt_utils.decode_token(invalid_token)

'''def test_increment_chat_count_limit():
    jwt_utils = JWTUtils()
    payload = {'chat_count': jwt_utils.max_chat_count, 'max_chat_count': jwt_utils.max_chat_count}
    token = jwt.encode(payload, jwt_utils.secret_key, algorithm=jwt_utils.algorithm)
    with pytest.raises(JWTException, match="Token chat limit exceeded"):
        jwt_utils.increment_chat_count(token)'''
