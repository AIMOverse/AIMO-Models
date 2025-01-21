from typing import Literal, List
from dataclasses import field
from pydantic_settings import BaseSettings


"""
Author: Jack Pan
Date: 2025-1-20
Description:
    This file is for settings of the application
"""


class Settings(BaseSettings):
    version:str = "1.0.0"
    API_V1_STR: str = f"/api/v{version}"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: List[str] = field(default_factory=lambda: ["*"])


    PROJECT_NAME: str = "AIMO-Models"


settings = Settings()  # type: ignore