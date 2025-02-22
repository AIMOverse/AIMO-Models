from app.exceptions.server_exceptions import ServerException


class AIMOException(ServerException):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        super().__init__(message, 500)
