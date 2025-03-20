import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.core.config import settings
from app.core.db import create_db_and_tables
from app.exception_handler.exception_handler import register_exception_handlers
from app.middleware.jwt_middleware import JWTMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.jwt_utils import JWTUtils

"""
Author: Jack Pan
Date: 2025-1-19
Description:
    This module implements a FastAPI app to provide a chat-based API endpoint.
    It integrates with the AIMO class to generate AI-powered responses based on user input.
    This is the controller of the app.
"""

# Configure logging settings
logging.basicConfig(
    level=logging.DEBUG if settings.ENVIRONMENT == 'local' else logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Custom function to generate unique IDs for API routes based on their tags and names.
    """
    return f"{route.tags[0]}-{route.name}"

# Initialize the FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,  # Title on generated documentation
    openapi_url=f"{settings.BASE_URL}/openapi.json",  # Path to generated OpenAPI documentation
    generate_unique_id_function=custom_generate_unique_id,  # Custom function for generating unique route IDs
    version=settings.version,  # Version of the API
    debug=True if settings.ENVIRONMENT == 'local' else False
)

# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # Allowed origins for CORS
    allow_credentials=True,  # Allow credentials in CORS
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"]  # Allow all headers
)

# Add Auth Middleware
app.add_middleware(JWTMiddleware,
                   base_url=settings.BASE_URL,
                   excluded_paths=settings.AUTH_EXCLUDE_PATHS)

# Add Rate Limit Middleware
app.add_middleware(
    RateLimitMiddleware,
    jwt_utils=JWTUtils(),
    excluded_paths=["/docs", "/redoc", "/openapi.json", "/api/v1/auth/login"]
)

# Register the exception handlers
register_exception_handlers(app)

# Include the API router with a prefix
app.include_router(api_router, prefix=settings.BASE_URL)


# Import the database initialization function
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
