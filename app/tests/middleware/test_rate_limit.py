import pytest
import jwt
import redis
import datetime
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import mocks needed for testing
from app.tests.mocks.redis_mock import MockRedis

# Ensure test configuration is imported
from app.tests.test_config import *

# Import components being tested
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.jwt_utils import JWTUtils

# Automatically set test environment variables
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["ADMIN_API_KEY"] = "test_admin_api_key"
    yield
    # Clean up after tests
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("SECRET_KEY", None)
    os.environ.pop("ADMIN_API_KEY", None)

# Create test application
@pytest.fixture
def app():
    app = FastAPI()
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "success"}
    
    @app.get("/excluded")
    def excluded_endpoint():
        return {"message": "excluded path"}
    
    return app

@pytest.fixture
def jwt_utils():
    return JWTUtils(algorithm='HS256')

@pytest.fixture
def valid_token(jwt_utils):
    payload = {"user_id": "test_user", "username": "tester"}
    return jwt_utils.generate_token(payload)

@pytest.fixture
def client(app, jwt_utils):
    app.add_middleware(
        RateLimitMiddleware,
        jwt_utils=jwt_utils,
        excluded_paths=["/excluded"]
    )
    return TestClient(app)

# Test request without token
def test_no_token(client):
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Rate-Limit-Limit" not in response.headers

# Test request with valid token
@patch('app.core.redis.RedisClient.get_client')
def test_valid_token(mock_get_client, client, valid_token):
    mock_redis = MockRedis()
    mock_get_client.return_value = mock_redis
    
    response = client.get(
        "/test",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    
    assert response.status_code == 200
    assert "X-Rate-Limit-Limit" in response.headers
    assert "X-Rate-Limit-Remaining" in response.headers
    assert "X-Rate-Limit-Reset" in response.headers

# Test excluded path
@patch('app.core.redis.RedisClient.get_client')
def test_excluded_path(mock_get_client, client, valid_token):
    mock_redis = MockRedis()
    mock_get_client.return_value = mock_redis
    
    response = client.get(
        "/excluded",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    
    assert response.status_code == 200
    assert "X-Rate-Limit-Limit" not in response.headers

# Test exceeding rate limit
@patch('app.core.redis.RedisClient.get_client')
def test_rate_limit_exceeded(mock_get_client, client, valid_token, jwt_utils):
    # Create a token with custom quota
    payload = {"user_id": "rate_limited_user"}
    low_quota_token = jwt_utils.generate_token(payload, custom_quota=2)
    
    # Mock Redis client returning count exceeding quota
    mock_redis = MockRedis()
    # Preset count to quota value
    jti = jwt.decode(
        low_quota_token, 
        jwt_utils.secret_key, 
        algorithms=[jwt_utils.algorithm]
    )["jti"]
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    key = f"rate_limit:{jti}:{today}"
    mock_redis.data[key] = '2'  # Already reached quota
    
    mock_get_client.return_value = mock_redis
    
    response = client.get(
        "/test",
        headers={"Authorization": f"Bearer {low_quota_token}"}
    )
    
    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded. Try again tomorrow."

# Test Redis connection error
@patch('app.core.redis.RedisClient.get_client')
def test_redis_error(mock_get_client, client, valid_token):
    # Mock Redis connection error
    mock_get_client.side_effect = redis.exceptions.RedisError("Connection failed")
    
    response = client.get(
        "/test",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    
    # Request should still succeed even with Redis error
    assert response.status_code == 200
