import json
import logging

from starlette.testclient import TestClient

from app.core.config import settings

"""
Author: Jack Pan
Date: 2025-1-20
Description:
    This file is for testing chat related APIs.
"""

# Test generate a response from the input
def test_generate(client: TestClient, get_access_token) -> None:
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
        url=f"{settings.BASE_URL}/chat/completions",
        json=data,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200


# Test SSE endpoint
def test_sse_chat(client: TestClient, get_access_token) -> None:
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
        url=f"{settings.BASE_URL}/chat/completions",
        json=data,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {get_access_token}"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    received_role = False
    received_content = False
    received_done = False
    event_count = 0
    error_count = 0
    max_errors = 3
    all_raw_lines = []

    for line in response.iter_lines():
        if not line:
            continue

        decoded_line = line.decode("utf-8") if isinstance(line, bytes) else line
        all_raw_lines.append(decoded_line)
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
            logging.debug(f"Attempting to parse JSON: {json_str}")
            
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
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
            if "content" in delta and delta["content"]:
                received_content = True
                logging.info(f"Received content: {delta['content']}")

        except json.JSONDecodeError as e:
            error_count += 1
            error_position = f"line 1 column {e.pos}" if hasattr(e, 'pos') else "unknown position"
            error_msg = f"JSON parse error: {e} at {error_position}"
            logging.error(f"{error_msg} for line: {json_str}")
            
            if error_count >= max_errors:
                all_lines_str = "\n".join(all_raw_lines)
                assert False, f"Too many JSON parsing errors ({error_count}). Last error: {error_msg}\nAll raw lines received:\n{all_lines_str}"
            continue
        except AssertionError as e:
            all_lines_str = "\n".join(all_raw_lines)
            logging.error(f"Assertion failed: {e}. JSON: {json_str}")
            assert False, f"Assertion error: {e}\nJSON: {json_str}\nAll raw lines:\n{all_lines_str}"

    logging.info(f"Test summary: events={event_count}, role={received_role}, content={received_content}, done={received_done}, errors={error_count}")
    
    if not received_content:
        all_lines_str = "\n".join(all_raw_lines)
        assert received_content, f"Did not receive any content. All raw lines received:\n{all_lines_str}"
    
    # Validation
    assert event_count > 0, "No events received"
    assert received_done, "Did not receive completion marker"