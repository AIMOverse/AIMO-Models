from app.exceptions.server_exceptions import ServerException


class AuthException(ServerException):
    """
    Exception class for authentication errors
    """

    def __init__(self, status_code: int, message: str = "authentication error"):
        super().__init__(message, status_code)
