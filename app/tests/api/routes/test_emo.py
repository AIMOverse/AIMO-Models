from starlette.testclient import TestClient

from app.core.config import settings


# Test emotion analysis endpoint
def test_analyze_emotion(client: TestClient, get_access_token):
    """Test normal emotion analysis case"""
    data = {
        "message": "I am feeling very happy today!"
    }
    response = client.post(
        url=f"{settings.BASE_URL}/emotion/analyze",
        json=data,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200
    result = response.json()
    # Only verify emotions field exists and is a list
    assert "emotions" in result
    assert isinstance(result["emotions"], list)
    # Verify that it contains expected emotion for happy message
    assert any(emotion in ["happiness", "joy"] for emotion in result["emotions"])