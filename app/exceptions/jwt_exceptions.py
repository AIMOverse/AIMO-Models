from app.exceptions.server_exceptions import ServerException


class JWTException(ServerException):
    """
    Exception class for JWT token errors
    """

    def __init__(self, message: str = "JWT token error"):
        super().__init__(message, 401)


class JWTException(Exception):
    """Exception raised for JWT token related errors"""
    pass
