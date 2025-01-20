from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.core.config import settings

"""
Author: Jack Pan
Date: 2025-1-19
Description:
    This module implements a FastAPI app to provide a chat-based API endpoint.
    It integrates with the AIMO class to generate AI-powered responses based on user input.
    This is the controller of the app.
"""



def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

# Initialize the FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME, # Title on generated document
    openapi_url=f"{settings.API_V1_STR}/openapi.json", # generated document path
    generate_unique_id_function=custom_generate_unique_id,
    version=settings.version
)

# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix=settings.API_V1_STR)
