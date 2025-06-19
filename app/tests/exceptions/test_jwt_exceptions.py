import pytest
from app.exceptions.jwt_exceptions import JWTException
from app.exceptions.server_exceptions import ServerException

def test_jwt_exception_default_init():
    """Test JWTException initialization with default parameters"""
    exc = JWTException()
    
    assert exc.message == "JWT token error"
    assert exc.status_code == 401
    assert isinstance(exc, ServerException)

def test_jwt_exception_custom_message():
    """Test JWTException initialization with custom message"""
    custom_message = "Custom JWT error"
    exc = JWTException(custom_message)
    
    assert exc.message == custom_message
    assert exc.status_code == 401
    assert isinstance(exc, ServerException)
