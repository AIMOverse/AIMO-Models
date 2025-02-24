import json
import pytest
from fastapi.testclient import TestClient
from app.core.config import settings
from app.main import app

"""
Author: Jack Pan, Wesley Xu
Date: 2025-1-20
Description:
    This file is for testing OpenAI-compatible chat API endpoints
"""

@pytest.fixture
def client():
    return TestClient(app)

def test_generate(client: TestClient) -> None:
    """Test non-streaming chat completion"""
    data = {
        "model": "aimo-chat",
        "messages": [
            {
                "role": "user",
                "content": "hi"
            }
        ],
        "temperature": 0.6,
        "max_tokens": 100,
        "stream": False
    }
    response = client.post(
        f"{settings.API_V1_STR}/chat/completions",  # Keep API path consistent with OpenAI
        json=data,
    )
    assert response.status_code == 200
    
    # Verify response structure
    json_response = response.json()
    assert "id" in json_response
    assert "choices" in json_response
    assert len(json_response["choices"]) > 0
    assert "message" in json_response["choices"][0]
    assert "content" in json_response["choices"][0]["message"]

def test_stream_chat(client: TestClient):
    """Test streaming chat completion"""
    data = {
        "model": "aimo-chat",
        "messages": [
            {
                "role": "user",
                "content": "hi"
            }
        ],
        "temperature": 0.6,
        "max_tokens": 100,
        "stream": True
    }

    response = client.post(
        f"{settings.API_V1_STR}/chat/completions",
        json=data,
        headers={"Accept": "text/event-stream"}
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    # Iterate response content line by line, parse SSE events
    valid_events = []
    for line in response.iter_lines():
        if not line:
            continue
            
        try:
            decoded_line = line.decode("utf-8") if isinstance(line, bytes) else line
            if not decoded_line.startswith("data: "):
                continue

            if decoded_line.strip() == "data: [DONE]":
                break  # SSE completion marker

            # Remove "data: " prefix
            json_str = decoded_line.replace("data: ", "").strip()
            if not json_str:
                continue

            # Parse JSON data
            event_data = json.loads(json_str)
            valid_events.append(event_data)

            # Verify SSE event data structure
            assert "choices" in event_data
            assert isinstance(event_data["choices"], list)
            assert len(event_data["choices"]) > 0
            assert "delta" in event_data["choices"][0]

        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON: {e}")
            continue

    # Verify at least one valid event was received
    assert len(valid_events) > 0, "No valid events received"
