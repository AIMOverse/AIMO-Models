import datetime
import os
import pytest
import jwt
from unittest.mock import patch, MagicMock

# Set environment variables for testing
os.environ["SECRET_KEY"] = "test_secret_key_for_testing"
os.environ["ACCESS_TOKEN_EXPIRE_TIME"] = "7"

from app.utils.jwt_utils import JWTUtils
from app.exceptions.jwt_exceptions import JWTException

"""
Author: Wesley
Date: 2023-3-13
Description:
    This file is for testing JWT utility functions.
"""

# Create a mock datetime class
class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return cls.mock_now
    
    @classmethod
    def utcnow(cls):
        return cls.mock_now

# Add a fixture for fixed time testing
@pytest.fixture
def fixed_time():
    return datetime.datetime(2023, 1, 1, 12, 0, 0)

@pytest.fixture
def jwt_utils():
    """
    Fixture to create JWTUtils instance
    """
    return JWTUtils(algorithm='HS256')

def test_init():
    """
    Test initialization of JWTUtils
    """
    utils = JWTUtils(algorithm='HS512')
    assert utils.secret_key == "test_secret_key_for_testing"
    assert utils.algorithm == 'HS512'
    assert utils.expire_time == 7

def test_generate_token(jwt_utils, fixed_time):
    """
    Test token generation
    """
    # Set up mock datetime
    MockDateTime.mock_now = fixed_time
    
    # Test payload
    payload = {"user_id": "123", "username": "testuser"}
    
    # Generate token with mocked time
    with patch('datetime.datetime', MockDateTime):
        token = jwt_utils.generate_token(payload)
    
    # Decode the token and verify contents - disable expiration validation 
    decoded = jwt.decode(
        token, 
        "test_secret_key_for_testing", 
        algorithms=['HS256'],
        options={"verify_exp": False}  # 禁用过期验证
    )
    assert decoded["user_id"] == "123"
    assert decoded["username"] == "testuser"
    
    # Verify expiration time
    expected_exp = int((fixed_time + datetime.timedelta(days=7)).timestamp())
    assert abs(decoded["exp"] - expected_exp) <= 1  # Allow 1 second difference due to processing time

def test_decode_token(jwt_utils):
    """
    Test token decoding
    """
    # Create a test token
    payload = {"user_id": "456", "username": "another_user"}
    exp = datetime.datetime.now() + datetime.timedelta(days=1)
    token = jwt.encode(
        {**payload, "exp": exp}, 
        "test_secret_key_for_testing", 
        algorithm='HS256'
    )
    
    # Decode and verify
    decoded = jwt_utils.decode_token(token)
    assert decoded["user_id"] == "456"
    assert decoded["username"] == "another_user"

def test_expired_token(jwt_utils, fixed_time):
    """
    Test handling of expired tokens
    """
    # Create an expired token
    payload = {"user_id": "789"}
    expired_time = fixed_time - datetime.timedelta(days=1)
    token = jwt.encode(
        {**payload, "exp": expired_time}, 
        "test_secret_key_for_testing", 
        algorithm='HS256'
    )
    
    # Attempt to decode the expired token
    with pytest.raises(JWTException) as exc_info:
        jwt_utils.decode_token(token)
    
    assert "Token expired" in str(exc_info.value)

def test_invalid_token(jwt_utils):
    """
    Test handling of invalid tokens
    """
    # Test with completely invalid token
    with pytest.raises(JWTException) as exc_info:
        jwt_utils.decode_token("invalid_token_string")
    
    assert "Invalid token" in str(exc_info.value)
    
    # Test with valid format but wrong signature
    payload = {"user_id": "123"}
    token = jwt.encode(payload, "wrong_secret_key", algorithm='HS256')
    
    with pytest.raises(JWTException) as exc_info:
        jwt_utils.decode_token(token)
    
    assert "Invalid token" in str(exc_info.value)

def test_algorithm_compatibility(jwt_utils):
    """
    Test compatibility with different algorithms
    """
    # Create a JWTUtils instance with HS512 algorithm
    hs512_utils = JWTUtils(algorithm='HS512')
    
    # Generate a token with HS512
    payload = {"user_id": "abc123"}
    token = hs512_utils.generate_token(payload)
    
    # The token should be decodable with the same instance
    decoded = hs512_utils.decode_token(token)
    assert decoded["user_id"] == "abc123"
    
    # But should fail with the default HS256 instance
    with pytest.raises(JWTException):
        jwt_utils.decode_token(token)
