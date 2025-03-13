from starlette.testclient import TestClient

from app.core.config import settings


# Test get available invitation codes
def test_get_available_invitation_codes(client: TestClient):
    """Test get available invitation codes"""
    response = client.get(
        f"{settings.BASE_URL}/invitation-code/get-available-invitation-codes",
        headers={"Content-Type": "application/json",
                 "api-key": settings.ADMIN_API_KEY},
    )
    assert response.status_code == 200
    result = response.json()
    # Only verify emotions field exists and is a list
    assert "invitation_codes" in result
    assert isinstance(result["invitation_codes"], list)
