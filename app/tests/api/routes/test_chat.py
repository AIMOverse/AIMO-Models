import json
import logging

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
        f"{settings.BASE_URL}/chat/completions",
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
        f"{settings.BASE_URL}/chat/completions",
        json=data,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
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

        # Remove 'data: ' prefix and clean the data
        json_str = decoded_line.replace("data: ", "").strip()
        if not json_str:
            continue

        # Handle various completion markers
        if json_str == "[DONE]":
            received_done = True
            logging.info("Received explicit DONE marker")
            continue

        try:
            # Replace single quotes with double quotes to ensure correct JSON format
            json_str = json_str.replace("'", '"')
            data = json.loads(json_str)
            
            # Check completion marker - additional section
            if "choices" in data and data["choices"] and \
               data["choices"][0].get("finish_reason") == "stop":
                received_done = True
                logging.info("Received finish_reason: stop")
                continue
                
            event_count += 1
            logging.debug(f"Parsed event {event_count}: {data}")

            # Validate event structure
            assert "choices" in data, "Missing choices in response"
            assert len(data["choices"]) > 0, "Empty choices array"
            assert "delta" in data["choices"][0], "Missing delta in choice"

            # Track message parts
            delta = data["choices"][0]["delta"]
            if "role" in delta and delta["role"] == "assistant":
                received_role = True
                logging.info("Received role event")
            elif "content" in delta and delta["content"].strip():
                received_content = True
                logging.info(f"Received content: {delta['content']}")

        except json.JSONDecodeError as e:
            logging.warning(f"JSON parse error: {e} for line: {json_str}")
            continue

    logging.info(f"Test summary: events={event_count}, role={received_role}, content={received_content}, done={received_done}")
    
    # Validation
    assert event_count > 0, "No events received"
    assert received_content, "Did not receive any content"
    assert received_done, "Did not receive completion marker"