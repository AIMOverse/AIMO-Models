import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_analyze_emotion(client: TestClient):
    """Test normal emotion analysis case"""
    data = {
        "message": "I am feeling very happy today!"
    }
    response = client.post(
        f"{settings.API_V1_STR}/emotion/analyze",
        json=data,
    )
    assert response.status_code == 200
    result = response.json()
    # Only verify emotions field exists and is a list
    assert "emotions" in result
    assert isinstance(result["emotions"], list)
    # Verify that it contains expected emotion for happy message
    assert any(emotion in ["happiness", "joy"] for emotion in result["emotions"])

def test_analyze_emotion_error_cases(client: TestClient):
    """Test error handling cases"""
    # Test missing message field
    invalid_data = {}
    response = client.post(
        f"{settings.API_V1_STR}/emotion/analyze",
        json=invalid_data,
    )
    assert response.status_code == 422
    error_detail = response.json()
    assert "detail" in error_detail
    # FastAPI validation error format includes a list of errors
    assert isinstance(error_detail["detail"], list)
    # Check the specific error message
    validation_error = error_detail["detail"][0]
    assert validation_error["type"] == "missing"
    assert validation_error["loc"] == ["body", "message"]
    assert "Field required" in validation_error["msg"]

    # Test empty message
    empty_data = {
        "message": "   "  # Only whitespace
    }
    response = client.post(
        f"{settings.API_V1_STR}/emotion/analyze",
        json=empty_data,
    )
    assert response.status_code == 200
    result = response.json()
    assert "emotions" in result
    assert isinstance(result["emotions"], list)