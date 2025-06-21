import pytest
from app.exceptions.aimo_exceptions import AIMOException
from app.exceptions.server_exceptions import ServerException

def test_aimo_exception_default_init():
    """Test AIMOException initialization with default parameters"""
    exc = AIMOException()
    
    assert exc.message == "Model error during processing"
    assert exc.status_code == 500
    assert isinstance(exc, ServerException)

def test_aimo_exception_custom_message():
    """Test AIMOException initialization with custom message"""
    custom_message = "AIMO model processing error"
    exc = AIMOException(custom_message)
    
    assert exc.message == custom_message
    assert exc.status_code == 500
    assert isinstance(exc, ServerException)
