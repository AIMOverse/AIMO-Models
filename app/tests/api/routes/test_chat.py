import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

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