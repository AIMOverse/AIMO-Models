import os
import pytest
from fastapi.testclient import TestClient

# Set the API key for testing before importing the FastAPI app
os.environ["NEBULA_API_KEY"] = "sk-irz6Mnu2ReWGMmSnqNPyMg"

from app.main import app
from app.core.config import settings

"""
Author: Jack Pan
Date: 2025-1-20
Description:
    This file is for testing chat related APIs.
"""

@pytest.fixture
def client():
    return TestClient(app)

# Test generate a response from the input
def test_generate(client: TestClient) -> None:
    data = {
        "messages": [
            {
                "role": "user",
                "content": "hi"
            }
        ],
        "temperature": 0.6,
        "max_new_tokens": 100
    }
    response = client.post(
        f"{settings.API_V1_STR}/chat/",
        json=data,
    )
    assert response.status_code == 200