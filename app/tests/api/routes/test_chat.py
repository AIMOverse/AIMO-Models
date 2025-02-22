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
        "max_new_tokens": 100,
        "stream": False
    }
    response = client.post(
        f"{settings.API_V1_STR}/chat/",
        json=data,
    )
    assert response.status_code == 200


# Test SSE endpoint
def test_sse_chat(client: TestClient):
    data = {
        "messages": [
            {
                "role": "user",
                "content": "hi"
            }
        ],
        "temperature": 0.6,
        "max_new_tokens": 100,
        "stream": True
    }
    response = client.post(
        f"{settings.API_V1_STR}/chat/",
        json=data,
    )

    # Check if the response is successful
    assert response.status_code == 200
    # Check if the response is in the correct format
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    events_received = []
    for line in response.iter_lines():
        if line.startswith("data: "):  # SSE format：data: xxx
            events_received.append(line[6:])  # Remove the "data: " prefix

    assert len(events_received) > 0  # Ensure that at least one event is received
    assert "content" in events_received[0] and "role" in events_received[0]  # Ensure that the first event is valid
