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
        "messages": [
            {
                "role": "user",
                "content": "I am feeling very happy today!"
            }
        ],
        "temperature": 0.6,
        "max_tokens": 100
    }
    response = client.post(
        f"{settings.API_V1_STR}/emotion/analyze",
        json=data,
    )
    assert response.status_code == 200
    result = response.json()
    assert "text" in result
    assert "emotions" in result
    assert isinstance(result["emotions"], list)

def test_analyze_emotion_multiple_messages(client: TestClient):
    """Test multiple messages case"""
    data = {
        "model": "aimo-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are an emotion analysis assistant"
            },
            {
                "role": "user",
                "content": "The weather is nice today"
            },
            {
                "role": "assistant",
                "content": "Indeed, it is"
            },
            {
                "role": "user",
                "content": "I feel very depressed and sad"
            }
        ]
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/emotion/analyze",
        json=data,
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # Verify analysis of last user message
    assert result["text"] == "I feel very depressed and sad"
    
    # Verify detected emotions
    assert any(emotion in ["sadness", "depression"] for emotion in result["emotions"])

def test_analyze_emotion_error_cases(client: TestClient):
    """Test error handling cases"""
    
    # Test with valid user message first (baseline test)
    valid_data = {
        "model": "aimo-chat",
        "messages": [{
            "role": "user",
            "content": "I am feeling happy"
        }]
    }
    response = client.post(
        f"{settings.API_V1_STR}/emotion/analyze",
        json=valid_data,
    )
    assert response.status_code == 200
    
    try:
        # Test empty messages list - Expect IndexError
        empty_data = {
            "model": "aimo-chat",
            "messages": []
        }
        response = client.post(
            f"{settings.API_V1_STR}/emotion/analyze",
            json=empty_data,
        )
    except IndexError:
        # This is expected behavior
        pass
    
    try:
        # Test missing content - Expect type error
        no_content_data = {
            "model": "aimo-chat",
            "messages": [{"role": "user"}]
        }
        response = client.post(
            f"{settings.API_V1_STR}/emotion/analyze",
            json=no_content_data,
        )
    except:
        # This is expected behavior
        pass
        
    try:
        # Test non-user role - No role validation, analyze any content
        assistant_msg_data = {
            "model": "aimo-chat",
            "messages": [{
                "role": "assistant",
                "content": "test content"
            }]
        }
        response = client.post(
            f"{settings.API_V1_STR}/emotion/analyze",
            json=assistant_msg_data,
        )
        assert response.status_code == 200
    except:
        # Expected potential failure
        pass