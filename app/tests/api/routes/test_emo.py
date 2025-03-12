import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


# Test emotion analysis endpoint
def test_analyze_emotion(client: TestClient):
    """Test normal emotion analysis case"""
    data = {
        "message": "I am feeling very happy today!"
    }
    response = client.post(
        f"{settings.BASE_URL}/emotion/analyze",
        json=data,
    )
    assert response.status_code == 200
    result = response.json()
    # Only verify emotions field exists and is a list
    assert "emotions" in result
    assert isinstance(result["emotions"], list)
    # Verify that it contains expected emotion for happy message
    assert any(emotion in ["happiness", "joy"] for emotion in result["emotions"])