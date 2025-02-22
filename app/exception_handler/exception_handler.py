from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from app.exceptions.server_exceptions import ServerException


def register_exception_handlers(app: FastAPI):
    """Global exception handlers for the FastAPI application."""

    @app.exception_handler(ServerException)
    async def custom_exception_handler(_request: Request, exc: ServerException):
        """
        Custom exception handler for ServerException.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(_request: Request, _exc: Exception):
        """
        Global exception handler for all uncaught exceptions.
        """
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"}
        )
