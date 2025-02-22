import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.core.config import settings
from app.exception_handler.exception_handler import register_exception_handlers

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
    level=logging.DEBUG,
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
    openapi_url=f"{settings.API_V1_STR}/openapi.json",  # Path to generated OpenAPI documentation
    generate_unique_id_function=custom_generate_unique_id,  # Custom function for generating unique route IDs
    version=settings.version  # Version of the API
)

# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # Allowed origins for CORS
    allow_credentials=True,  # Allow credentials in CORS
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"]  # Allow all headers
)

# Register the exception handlers
register_exception_handlers(app)

# Include the API router with a prefix
app.include_router(api_router, prefix=settings.API_V1_STR)
# Include the API router without a prefix
app.include_router(api_router)