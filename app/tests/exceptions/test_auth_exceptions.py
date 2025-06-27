import pytest
from app.exceptions.auth_exceptions import AuthException
from app.exceptions.server_exceptions import ServerException

def test_auth_exception_default_message():
    """Test AuthException initialization with default message"""
    status_code = 403
    exc = AuthException(status_code)
    
    assert exc.message == "authentication error"
    assert exc.status_code == status_code
    assert isinstance(exc, ServerException)

def test_auth_exception_custom_init():
    """Test AuthException initialization with custom parameters"""
    message = "Custom authentication error"
    status_code = 401
    exc = AuthException(status_code, message)
    
    assert exc.message == message
    assert exc.status_code == status_code
    assert isinstance(exc, ServerException)
