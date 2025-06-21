import pytest
from app.exceptions.server_exceptions import ServerException

def test_server_exception_init():
    """Test ServerException initialization"""
    message = "Server error"
    status_code = 500
    exc = ServerException(message, status_code)
    
    assert exc.message == message
    assert exc.status_code == status_code
    assert isinstance(exc, Exception)

def test_server_exception_inheritance():
    """Test ServerException inheritance"""
    exc = ServerException("Test message", 400)
    assert issubclass(ServerException, Exception)
