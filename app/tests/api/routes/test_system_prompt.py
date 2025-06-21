import pytest
from unittest.mock import patch

from starlette.testclient import TestClient
from fastapi import status

from app.core.config import settings

"""
Author: Wesley Xu
Date: 2025-06-19
Description:
    Tests for system-prompt–related APIs, rewritten so that real
    failures surface instead of being silently skipped.
"""

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_prompt_manager():
    """
    Automatically patch `app.api.routes.system_prompt.prompt_manager` for all tests.

    Individual tests can override the default return values dynamically
    via `mock_prompt_manager.get_prompt.return_value = ...`.
    """
    with patch("app.api.routes.system_prompt.prompt_manager") as manager:
        manager.get_prompt.return_value = {
            "self_cognition": "Test self cognition",
            "guidelines": "Test guidelines",
            "rules": "Test rules",
            "overall_style": "Test overall style",
        }
        manager.update_prompt.return_value = True
        manager.get_history.return_value = [
            {
                "id": 1,
                "timestamp": "2025-06-19T12:00:00",
                "modified_by": "System",
                "purpose": "Initial system prompt",
            }
        ]
        manager.get_history_prompt.return_value = {
            "self_cognition": "Historical self cognition",
            "guidelines": "Historical guidelines",
            "rules": "Historical rules",
            "overall_style": "Historical overall style",
        }
        yield manager


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_get_system_prompt(client: TestClient, get_access_token) -> None:
    """GET /get-system-prompt should return all four prompt sections."""
    resp = client.get(
        f"{settings.BASE_URL}/system-prompt/get-system-prompt",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_access_token}",
        },
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data.keys() >= {"self_cognition", "guidelines", "rules", "overall_style"}


def test_get_system_prompt_section(
    client: TestClient, get_access_token, mock_prompt_manager
) -> None:
    """GET ?section=xxx should return only the specific section."""
    section = "self_cognition"
    # Override the default mock return value for this specific test
    mock_prompt_manager.get_prompt.return_value = {section: "Test self cognition"}

    resp = client.get(
        f"{settings.BASE_URL}/system-prompt/get-system-prompt?section={section}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_access_token}",
        },
    )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {section: "Test self cognition"}


def test_change_system_prompt(client: TestClient, get_access_token) -> None:
    """POST /change-system-prompt should succeed and return a standard success structure."""
    payload = {
        "section": "rules",
        "content": "This is a test rule update.",
        "modified_by": "TestUser",
        "purpose": "Testing update functionality",
    }

    resp = client.post(
        f"{settings.BASE_URL}/system-prompt/change-system-prompt",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_access_token}",
        },
    )

    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body == {"status": "success", "code": 200}


def test_review_history_prompt(client: TestClient, get_access_token) -> None:
    """GET /review-history-prompt should return a list of history entries with metadata."""
    resp = client.get(
        f"{settings.BASE_URL}/system-prompt/review-history-prompt",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_access_token}",
        },
    )

    assert resp.status_code == status.HTTP_200_OK
    history = resp.json()
    assert isinstance(history, list)

    if history:
        first = history[0]
        assert first.keys() >= {"id", "timestamp", "modified_by", "purpose"}


def test_select_history_prompt(
    client: TestClient, get_access_token, mock_prompt_manager
) -> None:
    """GET /select-history-prompt/{id} should return a specific version of the prompt."""
    history_id = 1
    mock_prompt_manager.get_history_prompt.return_value = {
        "self_cognition": "Historical self cognition",
        "guidelines": "Historical guidelines",
        "rules": "Historical rules",
        "overall_style": "Historical overall style",
    }

    resp = client.get(
        f"{settings.BASE_URL}/system-prompt/select-history-prompt/{history_id}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_access_token}",
        },
    )

    assert resp.status_code == status.HTTP_200_OK
    prompt = resp.json()
    assert prompt.keys() >= {
        "self_cognition",
        "guidelines",
        "rules",
        "overall_style",
    }
