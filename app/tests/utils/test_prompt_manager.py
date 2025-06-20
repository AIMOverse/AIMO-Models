import pytest
import json
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.utils.prompt_manager import PromptManager

"""
Author: Wesley Xu
Date: 2025-6-19
Description:
    This file is for testing the PromptManager utility class.
"""

@pytest.fixture
def mock_redis():
    """Create a mock Redis client"""
    # Store data in memory to simulate Redis storage
    data_store = {}
    list_store = {}
    
    # Create mock Redis client
    mock_redis = MagicMock()
    
    # Mock Redis methods
    def mock_exists(key):
        return key in data_store
    
    def mock_get(key):
        return data_store.get(key)
    
    def mock_set(key, value):
        data_store[key] = value
        return True
    
    def mock_llen(key):
        return len(list_store.get(key, []))
    
    def mock_lrange(key, start, end):
        items = list_store.get(key, [])
        # Redis lrange includes the end index
        end = min(end, len(items) - 1) if end >= 0 else len(items) + end
        return items[start:end + 1]
    
    def mock_rpush(key, value):
        if key not in list_store:
            list_store[key] = []
        list_store[key].append(value)
        return len(list_store[key])
    
    # Configure mock methods
    mock_redis.exists.side_effect = mock_exists
    mock_redis.get.side_effect = mock_get
    mock_redis.set.side_effect = mock_set
    mock_redis.llen.side_effect = mock_llen
    mock_redis.lrange.side_effect = mock_lrange
    mock_redis.rpush.side_effect = mock_rpush
    
    return mock_redis

@pytest.fixture
def prompt_manager(mock_redis):
    """Create a PromptManager instance using mock Redis"""
    # Set the testing environment variable
    os.environ["TESTING"] = "True"
    
    # Pass mock_redis directly instead of patching Redis class
    manager = PromptManager(redis_client=mock_redis)
    yield manager
    
    # Clean up the environment variable
    os.environ.pop("TESTING", None)

def test_initialization(mock_redis):
    """Test PromptManager initialization"""
    # Set the testing environment variable
    os.environ["TESTING"] = "True"
    
    # Pass mock_redis directly
    manager = PromptManager(redis_client=mock_redis)
    
    # It should call Redis exists method to check if current prompt exists
    mock_redis.exists.assert_called_with("current_prompt")
    
    # Clean up the environment variable
    os.environ.pop("TESTING", None)

def test_get_prompt_all_sections(prompt_manager, mock_redis):
    """Test retrieving the complete system prompt"""
    # Get the complete prompt
    prompt = prompt_manager.get_prompt()
    
    # Verify all sections exist
    assert "self_cognition" in prompt
    assert "guidelines" in prompt
    assert "rules" in prompt
    assert "overall_style" in prompt
    assert "complete_prompt" in prompt
    
    # Verify the complete prompt is a combination of all sections
    expected_complete = (
        prompt["self_cognition"] +
        prompt["guidelines"] +
        prompt["rules"] +
        prompt["overall_style"]
    )
    assert prompt["complete_prompt"] == expected_complete

def test_get_prompt_specific_section(prompt_manager, mock_redis):
    """Test retrieving a specific section of the system prompt"""
    # Get a specific section
    section_prompt = prompt_manager.get_prompt("self_cognition")
    
    # Verify it returns a dictionary containing only the requested section
    assert isinstance(section_prompt, dict)
    assert "self_cognition" in section_prompt
    assert len(section_prompt) == 1
    
    # Test with an invalid section name
    with pytest.raises(ValueError):
        prompt_manager.get_prompt("invalid_section")

def test_update_prompt(prompt_manager, mock_redis):
    """Test updating the system prompt"""
    # Update the rules section
    new_content = "Test rules content"
    
    # Mock getting current prompt and history
    current_prompt = {
        "self_cognition": "I am an AI assistant.",
        "guidelines": "I try to be helpful and accurate.",
        "rules": "I follow ethical guidelines.",
        "overall_style": "I am friendly and concise.",
        "complete_prompt": "I am an AI assistant. I try to be helpful and accurate. I follow ethical guidelines. I am friendly and concise."
    }
    
    # Set mock behavior
    mock_redis.get.side_effect = lambda key: json.dumps(current_prompt) if key == "current_prompt" else json.dumps([]) if key == "prompt_history" else None
    
    # Execute update
    result = prompt_manager.update_prompt("rules", new_content, "Test User", "Testing update")
    
    # Verify update was successful
    assert result is True
    
    # Verify Redis set method was called
    mock_redis.set.assert_called()

def test_get_history(prompt_manager, mock_redis):
    """Test retrieving the prompt history"""
    # Prepare mock history data
    history_data = [
        {
            "id": 1,
            "timestamp": datetime.now().isoformat(),
            "modified_by": "System",
            "purpose": "Initial system prompt",
            "prompt": {}
        }
    ]
    
    # Set mock behavior
    mock_redis.get.return_value = json.dumps(history_data)
    
    # Get history
    history = prompt_manager.get_history()
    
    # Verify history
    assert len(history) == 1
    assert history[0]["id"] == 1
    assert "timestamp" in history[0]
    assert history[0]["modified_by"] == "System"
    assert history[0]["purpose"] == "Initial system prompt"

def test_get_history_prompt(prompt_manager, mock_redis):
    """Test retrieving a specific history version of the prompt"""
    # This test requires mocking multiple history versions
    pass

def test_update_all_sections(prompt_manager, mock_redis):
    """Test updating all prompt sections"""
    # Prepare new prompt content
    new_prompt = {
        "self_cognition": "New self cognition",
        "guidelines": "New guidelines",
        "rules": "New rules",
        "overall_style": "New style"
    }
    
    # Execute update
    result = prompt_manager.update_all_sections(new_prompt, "Test User", "Complete update")
    
    # Verify update was successful
    assert result is True
    
    # Verify Redis set method was called
    mock_redis.set.assert_called()
    
    # Verify all sections were updated
    updated_prompt = prompt_manager.get_prompt()
    for section, content in new_prompt.items():
        assert updated_prompt[section] == content

def test_update_all_sections_invalid_input(prompt_manager):
    """Test updating all sections with invalid input"""
    # Prepare invalid prompt content (missing a section)
    new_prompt = {
        "self_cognition": "New self cognition",
        "guidelines": "New guidelines",
        # Missing 'rules' and 'overall_style'
    }
    
    # Execute update and expect it to raise ValueError
    with pytest.raises(ValueError, match="All sections must be provided"):
        prompt_manager.update_all_sections(new_prompt, "Test User", "Invalid update")

def test_get_history_prompt_invalid_id(prompt_manager):
    """Test retrieving a history prompt with an invalid ID"""
    # Execute get_history_prompt with an invalid ID
    with pytest.raises(ValueError, match="Invalid history ID"):
        prompt_manager.get_history_prompt(-1)
    
    # Also test with a non-existent ID
    with pytest.raises(ValueError, match="History entry not found"):
        prompt_manager.get_history_prompt(9999)

def test_get_history_prompt_valid_id(prompt_manager, mock_redis):
    """Test retrieving a valid history prompt"""
    # Prepare mock history data
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "modified_by": "System",
        "purpose": "Initial system prompt",
        "prompt": {
            "self_cognition": "Historical self cognition",
            "guidelines": "Historical guidelines",
            "rules": "Historical rules",
            "overall_style": "Historical overall style"
        }
    }
    
    # Set the history directly in the prompt_manager
    prompt_manager.history = [history_entry]
    
    # Get history prompt by ID
    history_prompt = prompt_manager.get_history_prompt(1)
    
    # Verify the retrieved prompt matches the historical data
    assert history_prompt["self_cognition"] == "Historical self cognition"
    assert history_prompt["guidelines"] == "Historical guidelines"
    assert history_prompt["rules"] == "Historical rules"
    assert history_prompt["overall_style"] == "Historical overall style"

def test_load_or_initialize_new_prompt(mock_redis):
    """Test initializing when no prompt exists in Redis"""
    # Set Redis to indicate that the current prompt doesn't exist
    mock_redis.exists.return_value = False
    
    # Initialize PromptManager
    os.environ["TESTING"] = "True"
    manager = PromptManager(redis_client=mock_redis)
    
    # Verify that Redis exists method was called
    mock_redis.exists.assert_called_with("current_prompt")
    
    # Verify that a default prompt was created
    assert "self_cognition" in manager.current_prompt
    assert "guidelines" in manager.current_prompt
    assert "rules" in manager.current_prompt
    assert "overall_style" in manager.current_prompt
    
    # Verify that _save_current_prompt was called to save the default prompt to Redis
    mock_redis.set.assert_called_once()
    
    # Clean up environment variable
    os.environ.pop("TESTING", None)

def test_load_or_initialize_existing_prompt():
    """Test loading existing prompt from Redis"""
    # Prepare mock existing prompt data
    existing_prompt = {
        "self_cognition": "Existing self cognition",
        "guidelines": "Existing guidelines",
        "rules": "Existing rules",
        "overall_style": "Existing overall style"
    }
    
    # Use patch to directly mock Redis methods
    with patch('redis.Redis') as mock_redis_class:
        # Set up mock instance
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        
        # Set Redis to return existing prompt as valid JSON
        mock_redis.exists.return_value = True
        mock_redis.get.return_value = json.dumps(existing_prompt)
        mock_redis.llen.return_value = 0
        
        # Initialize PromptManager
        os.environ["TESTING"] = "False"  # Use the actual Redis connection flow
        manager = PromptManager()
        
        # Verify that the loaded prompt matches the expected one
        assert manager.current_prompt["self_cognition"] == "Existing self cognition"
        assert manager.current_prompt["guidelines"] == "Existing guidelines"
        assert manager.current_prompt["rules"] == "Existing rules"
        assert manager.current_prompt["overall_style"] == "Existing overall style"
        
        # Verify that Redis methods were called
        mock_redis.exists.assert_called()
        mock_redis.get.assert_called()
        
        # Clean up environment variable
        os.environ.pop("TESTING", None)

def test_load_or_initialize_invalid_json():
    """Test loading with invalid JSON in Redis"""
    # Use patch to directly mock Redis methods
    with patch('redis.Redis') as mock_redis_class:
        # Set up mock instance
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        
        # Set Redis to return invalid JSON for current prompt
        mock_redis.exists.return_value = True
        mock_redis.get.return_value = "invalid json data"
        mock_redis.llen.return_value = 0
        
        # Initialize PromptManager
        os.environ["TESTING"] = "False"  # Use the actual Redis connection flow
        manager = PromptManager()
        
        # Verify that a default prompt was created (because JSON parsing failed)
        assert "self_cognition" in manager.current_prompt
        assert "guidelines" in manager.current_prompt
        assert "rules" in manager.current_prompt
        assert "overall_style" in manager.current_prompt
        
        # Verify that Redis methods were called
        mock_redis.exists.assert_called()
        mock_redis.get.assert_called()
        
        # Clean up environment variable
        os.environ.pop("TESTING", None)

def test_load_or_initialize_none_value():
    """Test loading when Redis returns None"""
    # Use patch to directly mock Redis methods
    with patch('redis.Redis') as mock_redis_class:
        # Set up mock instance
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        
        # Set Redis to return None for current prompt
        mock_redis.exists.return_value = True
        mock_redis.get.return_value = None
        mock_redis.llen.return_value = 0
        
        # Initialize PromptManager
        os.environ["TESTING"] = "False"  # Use the actual Redis connection flow
        manager = PromptManager()
        
        # Verify that a default prompt was created (because Redis returned None)
        assert "self_cognition" in manager.current_prompt
        assert "guidelines" in manager.current_prompt
        assert "rules" in manager.current_prompt
        assert "overall_style" in manager.current_prompt
        
        # Verify that Redis methods were called
        mock_redis.exists.assert_called()
        mock_redis.get.assert_called()
        
        # Clean up environment variable
        os.environ.pop("TESTING", None)