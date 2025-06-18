import os
import socket
from dataclasses import field
from typing import Literal, List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

"""
Author: Jack Pan
Date: 2025-1-20
Description:
    This file is for settings of the application
"""

# load .env file
load_dotenv()


class Settings(BaseSettings):
    version: str = "1.0.0"  # Version of the API
    BASE_URL: str = f"/api/v{version}"  # Path to the base API
    ENVIRONMENT: Literal[
        "local", "staging", "production"] = "production" if "ai-model-service" in socket.gethostname() else "local"  # Environment of the application

    BACKEND_CORS_ORIGINS: List[str] = field(default_factory=lambda: ["*"])  # Allowed origins for CORS

    PROJECT_NAME: str = "AIMO-Models"  # Title on generated documentation

    # LLM API KEY
    NEBULA_API_KEY: str = os.environ.get("NEBULA_API_KEY")

    # JWT Secret Key
    SECRET_KEY: str = os.environ.get("SECRET_KEY")

    # JWT Expire Time
    ACCESS_TOKEN_EXPIRE_TIME: int = 3  # days

    # Invitation Code Expire Time
    INVITATION_CODE_EXPIRE_TIME: int = 7  # days

    # Authentication Excludes Paths
    AUTH_EXCLUDE_PATHS: List[str] = field(
        default_factory=lambda: ["/auth/check-invitation-code",
                                 "/invitation-code/generate-invitation-code",
                                 "/invitation-code/get-available-invitation-codes"])

    # Admin API Key
    ADMIN_API_KEY: str = os.environ.get("ADMIN_API_KEY")

    # Database URL
    DATABASE_URL: str = os.environ.get("DATABASE_URL")


settings = Settings()
