import os
import socket
from dataclasses import field
from typing import Literal, List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

"""
Author: Jack Pan, Wesley Xu
Date: 2025-7-10
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
    REDPILL_API_KEY: str = os.environ.get("REDPILL_API_KEY")

    # JWT Secret Key
    SECRET_KEY: str = os.environ.get("SECRET_KEY")

    # Listmonk Settings
    LISTMONK_API_URL: str = os.environ.get("LISTMONK_API_URL")
    LISTMONK_API_KEY: str = os.environ.get("LISTMONK_API_KEY")
    LISTMONK_USERNAME: str = os.environ.get("LISTMONK_USERNAME")
    LISTMONK_PASSWORD: str = os.environ.get("LISTMONK_PASSWORD")
    DEFAULT_SENDER_EMAIL: str = os.environ.get("DEFAULT_SENDER_EMAIL")
    DEFAULT_SENDER_NAME: str = os.environ.get("DEFAULT_SENDER_NAME")
    LISTMONK_INVITATION_TEMPLATE_ID: int = int(os.environ.get("LISTMONK_INVITATION_TEMPLATE_ID"))
    
    # Email Settings
    EMAIL_LOGIN_EXPIRE_TIME: int = 30  # minutes

    # JWT Expire Time
    ACCESS_TOKEN_EXPIRE_TIME: int = 3  # days

    # Invitation Code Expire Time
    INVITATION_CODE_EXPIRE_TIME: int = 7  # days
    BOUND_INVITATION_CODE_EXPIRE_TIME: int = 365  # days

    # Authentication Excludes Paths
    AUTH_EXCLUDE_PATHS: List[str] = field(
        default_factory=lambda: ["/auth/check-invitation-code",
                                 "/auth/wallet-verify",
                                 "/auth/bind-invitation-code",
                                 "/auth/email-login",
                                 "/invitation-code/generate-invitation-code",
                                 "/invitation-code/get-available-invitation-codes"])

    # Admin API Key
    ADMIN_API_KEY: str = os.environ.get("ADMIN_API_KEY")

    # Database URL
    DATABASE_URL: str = os.environ.get("DATABASE_URL")

    # Redis
    REDIS_HOST: str = os.environ.get("REDIS_HOST")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT"))

    # Privy API Key
    PRIVY_APP_ID: str = os.environ.get("PRIVY_APP_ID")
    PRIVY_APP_SECRET: str = os.environ.get("PRIVY_APP_SECRET")


settings = Settings()
