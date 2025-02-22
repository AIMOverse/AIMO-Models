from app.exceptions.server_exceptions import ServerException


class AIMOException(ServerException):
    """Base class for exceptions for AIMO Model."""

    def __init__(self, message: str = "Model error during processing"):
        super().__init__(message, 500)
