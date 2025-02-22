class ServerException(Exception):
    """
    Base class for exceptions for the FastAPI application
    """
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
