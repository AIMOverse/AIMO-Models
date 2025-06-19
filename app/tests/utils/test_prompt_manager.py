import json
import os
import tempfile
import pytest
from datetime import datetime

from app.utils.prompt_manager import PromptManager

"""
Author: Wesley Xu
Date: 2025-6-19
Description:
    This file is for testing the PromptManager utility class.
"""

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def prompt_manager(temp_dir):
    """Create a PromptManager instance using a temporary directory"""
    return PromptManager(data_dir=temp_dir)

def test_initialization(temp_dir):
    """Test PromptManager initialization"""
    # When initializing a PromptManager
    manager = PromptManager(data_dir=temp_dir)
    
    # It should create default prompt files
    assert os.path.exists(os.path.join(temp_dir, "current_prompt.json"))
    assert os.path.exists(os.path.join(temp_dir, "prompt_history.json"))
    
    # Verify initial prompt content
    with open(os.path.join(temp_dir, "current_prompt.json"), 'r', encoding='utf-8') as f:
        current_prompt = json.load(f)
        assert "self_cognition" in current_prompt
        assert "guidelines" in current_prompt
        assert "rules" in current_prompt
        assert "overall_style" in current_prompt

def test_get_prompt_all_sections(prompt_manager):
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

def test_get_prompt_specific_section(prompt_manager):
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

def test_update_prompt(prompt_manager):
    """Test updating the system prompt"""
    # Update the rules section
    new_content = "Test rules content"
    result = prompt_manager.update_prompt("rules", new_content, "Test User", "Testing update")
    
    # Verify update was successful
    assert result is True
    
    # Verify content was updated
    updated_prompt = prompt_manager.get_prompt()
    assert updated_prompt["rules"] == new_content
    
    # Test with an invalid section name
    with pytest.raises(ValueError):
        prompt_manager.update_prompt("invalid_section", "content", "user", "purpose")

def test_get_history(prompt_manager):
    """Test retrieving the prompt history"""
    # After initialization, there should be one history entry
    history = prompt_manager.get_history()
    assert len(history) == 1
    assert history[0]["id"] == 1
    assert "timestamp" in history[0]
    assert history[0]["modified_by"] == "System"
    assert history[0]["purpose"] == "Initial system prompt"
    
    # After updating a prompt, history should increase
    prompt_manager.update_prompt("rules", "New rules", "Test User", "Test update")
    history = prompt_manager.get_history()
    assert len(history) == 2
    assert history[0]["id"] == 2  # Newest first
    assert history[0]["modified_by"] == "Test User"
    assert history[0]["purpose"] == "Test update"

def test_get_history_prompt(prompt_manager):
    """Test retrieving a specific historical version of the prompt"""
    # First create multiple history versions
    prompt_manager.update_prompt("rules", "Rules v2", "User1", "Update 1")
    prompt_manager.update_prompt("guidelines", "Guidelines v2", "User2", "Update 2")
    
    # Get the latest history version
    latest_history = prompt_manager.get_history_prompt(1)
    assert latest_history["rules"] == "Rules v2"
    assert latest_history["guidelines"] == "Guidelines v2"
    
    # Get the second newest history version
    second_history = prompt_manager.get_history_prompt(2)
    assert second_history["rules"] == "Rules v2"
    assert second_history["guidelines"] != "Guidelines v2"  # This version hasn't updated guidelines yet
    
    # Test with an invalid history ID
    with pytest.raises(ValueError):
        prompt_manager.get_history_prompt(100)  # Non-existent ID

def test_update_all_sections(prompt_manager):
    """Test updating all sections at once"""
    # Create a complete prompt string
    complete_prompt = (
        "══════════════════════════════\n"
        "Self-Cognition\n"
        "══════════════════════════════\n"
        "Test self-cognition content\n"
        "══════════════════════════════\n"
        "GUIDELINES\n"
        "══════════════════════════════\n"
        "Test guidelines content\n"
        "══════════════════════════════\n"
        "RULES\n"
        "══════════════════════════════\n"
        "Test rules content\n"
        "══════════════════════════════\n"
        "OVERALL STYLE\n"
        "══════════════════════════════\n"
        "Test overall style content\n"
        "══════════════════════════════\n"
    )
    
    # Update all sections
    result = prompt_manager.update_prompt("all", complete_prompt, "Test User", "Complete update")
    
    # Verify update was successful
    assert result is True
    
    # Verify all sections were updated
    updated_prompt = prompt_manager.get_prompt()
    assert "Test self-cognition content" in updated_prompt["self_cognition"]
    assert "Test guidelines content" in updated_prompt["guidelines"]
    assert "Test rules content" in updated_prompt["rules"]
    assert "Test overall style content" in updated_prompt["overall_style"]
