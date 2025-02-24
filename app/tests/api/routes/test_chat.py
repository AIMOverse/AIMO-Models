import json
import logging
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

    received_role = False
    received_content = False
    received_done = False
    event_count = 0

    for line in response.iter_lines():
        if not line:
            continue

        decoded_line = line.decode("utf-8") if isinstance(line, bytes) else line
        logging.debug(f"Raw line: {decoded_line}")

        if not decoded_line.startswith("data: "):
            continue

        # Remove all "data: " prefixes
        clean_line = decoded_line.replace("data: data: ", "data: ").strip()
        
        # Handle DONE marker - special case
        if clean_line in ["data: [DONE]", "data: [DONE]\n\n"]:
            received_done = True
            logging.info("Received DONE marker")
            break

        try:
            json_str = clean_line.replace("data: ", "").strip()
            if not json_str:
                continue

            data = json.loads(json_str)
            event_count += 1
            logging.debug(f"Parsed event {event_count}: {data}")

            # Check event structure
            assert "choices" in data
            assert len(data["choices"]) > 0
            assert "delta" in data["choices"][0]

            # Track message parts
            delta = data["choices"][0]["delta"]
            if "role" in delta and delta["role"] == "assistant":
                received_role = True
                logging.info("Received role event")
            if "content" in delta and delta["content"].strip():
                received_content = True
                logging.info(f"Received content: {delta['content']}")

        except json.JSONDecodeError as e:
            logging.warning(f"JSON parse error: {e} for line: {clean_line}")
            continue

    # Verify we got everything we needed
    assert event_count > 0, "No events received"
    assert received_role, "Did not receive role message"
    assert received_content, "Did not receive any content"
    assert received_done, "Did not receive DONE marker"
