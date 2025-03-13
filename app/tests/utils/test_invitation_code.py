import datetime
import json
import os
import pytest
from unittest.mock import patch, MagicMock

os.environ["SECRET_KEY"] = "test_secret_key_for_testing"
os.environ["ADMIN_API_KEY"] = "test_admin_api_key_for_testing"
os.environ["INVITATION_CODE_EXPIRE_TIME"] = "7"

from app.utils.invitation_code_utils import InvitationCodeUtils
from app.entity.invitation_code import InvitationCode

"""
Author: Wesley Xu
Date: 2025-3-13
Description:
    This file is for testing invitation code related utilities.
"""

# Test file path
TEST_FILE_PATH = "test_invitation_code.json"

# Create a mock datetime class
class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls):
        return cls.mock_now

# Add a fixture for fixed time testing
@pytest.fixture
def fixed_time():
    return datetime.datetime(2023, 1, 1, 12, 0, 0)

@pytest.fixture
def setup_teardown():
    """
    Fixture to create and delete test file before and after tests
    """
    # Before test
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
    
    yield  # Execute test
    
    # Cleanup after test
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)


@pytest.fixture
def invitation_code_utils():
    """
    Fixture to create InvitationCodeUtils instance
    """
    return InvitationCodeUtils(file_path=TEST_FILE_PATH)


def test_init():
    """
    Test initialization
    """
    utils = InvitationCodeUtils(file_path="custom_path.json")
    assert utils.file_path == "custom_path.json"


def test_get_invitation_codes_empty_file(setup_teardown, invitation_code_utils):
    """
    Test getting invitation codes from non-existent or empty file
    """
    # Test non-existent file
    codes = invitation_code_utils._get_invitation_codes()
    assert isinstance(codes, list)
    assert len(codes) == 0
    
    # Create empty file
    with open(TEST_FILE_PATH, "w") as f:
        f.write("")
    
    # Test empty file
    codes = invitation_code_utils._get_invitation_codes()
    assert isinstance(codes, list)
    assert len(codes) == 0


def test_save_and_get_invitation_codes(setup_teardown, invitation_code_utils):
    """
    Test saving and retrieving invitation codes
    """
    # Create test invitation codes
    now = datetime.datetime.now()
    expiration_time = now + datetime.timedelta(days=7)
    code1 = InvitationCode(code="TEST001", expiration_time=expiration_time, used=False)
    code2 = InvitationCode(code="TEST002", expiration_time=expiration_time, used=True)
    
    # Save invitation codes
    invitation_code_utils._save_invitation_codes([code1, code2])
    
    # Verify file content
    with open(TEST_FILE_PATH, "r") as f:
        content = json.load(f)
        assert "invitation_codes" in content
        assert len(content["invitation_codes"]) == 2
        assert content["invitation_codes"][0]["code"] == "TEST001"
        assert content["invitation_codes"][1]["code"] == "TEST002"
    
    # Retrieve and verify
    loaded_codes = invitation_code_utils._get_invitation_codes()
    assert len(loaded_codes) == 2
    assert loaded_codes[0].code == "TEST001"
    assert loaded_codes[1].code == "TEST002"
    assert loaded_codes[0].used is False
    assert loaded_codes[1].used is True


def test_generate_invitation_code(setup_teardown, invitation_code_utils, fixed_time):
    """
    Test generating invitation code
    """
    # Use fixed datetime
    future_time = fixed_time + datetime.timedelta(days=7)
    
    # Correctly mock datetime.now
    MockDateTime.mock_now = fixed_time
    with patch('datetime.datetime', MockDateTime):
        with patch('app.core.config.settings', INVITATION_CODE_EXPIRE_TIME=7):
            with patch('random.choices', return_value=list("TESTCODE")):
                # Generate invitation code
                invitation_code = invitation_code_utils.generate_invitation_code()
                
                # Verify invitation code
                assert invitation_code.code == "TESTCODE"
                assert invitation_code.expiration_time == future_time
                assert invitation_code.used is False
                
                # Verify it was saved to file
                saved_codes = invitation_code_utils._get_invitation_codes()
                assert len(saved_codes) == 1
                assert saved_codes[0].code == "TESTCODE"


def test_check_invitation_code(setup_teardown, invitation_code_utils, fixed_time):
    """
    Test invitation code verification
    """
    # Create test data
    now = fixed_time  # Use fixed datetime
    valid_code = InvitationCode(
        code="VALID", 
        expiration_time=now + datetime.timedelta(days=7),
        used=False
    )
    expired_code = InvitationCode(
        code="EXPIRED", 
        expiration_time=now - datetime.timedelta(days=1),
        used=False
    )
    used_code = InvitationCode(
        code="USED", 
        expiration_time=now + datetime.timedelta(days=7),
        used=True
    )
    
    # Save test data
    invitation_code_utils._save_invitation_codes([valid_code, expired_code, used_code])
    
    # Test valid invitation code
    MockDateTime.mock_now = now
    with patch('datetime.datetime', MockDateTime):
        assert invitation_code_utils.check_invitation_code("VALID") is True
        
        # Verify code is marked as used
        updated_codes = invitation_code_utils._get_invitation_codes()
        valid_code_updated = next((c for c in updated_codes if c.code == "VALID"), None)
        assert valid_code_updated.used is True
    
    # Test expired invitation code
    MockDateTime.mock_now = now
    with patch('datetime.datetime', MockDateTime):
        assert invitation_code_utils.check_invitation_code("EXPIRED") is False
    
    # Test used invitation code
    assert invitation_code_utils.check_invitation_code("USED") is False
    
    # Test non-existent invitation code
    assert invitation_code_utils.check_invitation_code("NONEXISTENT") is False


def test_get_available_invitation_codes(setup_teardown, invitation_code_utils, fixed_time):
    """
    Test retrieving available invitation codes
    """
    # Create test data
    now = fixed_time  # Use fixed datetime
    valid_code1 = InvitationCode(
        code="VALID1", 
        expiration_time=now + datetime.timedelta(days=7),
        used=False
    )
    valid_code2 = InvitationCode(
        code="VALID2", 
        expiration_time=now + datetime.timedelta(days=7),
        used=False
    )
    expired_code = InvitationCode(
        code="EXPIRED", 
        expiration_time=now - datetime.timedelta(days=1),
        used=False
    )
    used_code = InvitationCode(
        code="USED", 
        expiration_time=now + datetime.timedelta(days=7),
        used=True
    )
    
    # Save test data
    invitation_code_utils._save_invitation_codes([valid_code1, valid_code2, expired_code, used_code])
    
    # Get and verify available codes
    MockDateTime.mock_now = now
    with patch('datetime.datetime', MockDateTime):
        available_codes = invitation_code_utils.get_available_invitation_codes()
        assert len(available_codes) == 2
        assert "VALID1" in available_codes
        assert "VALID2" in available_codes
        assert "EXPIRED" not in available_codes
        assert "USED" not in available_codes


def test_duplicate_code_handling(setup_teardown, invitation_code_utils, fixed_time):
    """
    Test handling of duplicate invitation codes
    """
    # First save an invitation code
    now = fixed_time  # Use fixed datetime
    existing_code = InvitationCode(
        code="TESTCODE", 
        expiration_time=now + datetime.timedelta(days=7),
        used=False
    )
    invitation_code_utils._save_invitation_codes([existing_code])
    
    # Mock random.choices to return existing code first, then new code
    MockDateTime.mock_now = now
    with patch('datetime.datetime', MockDateTime):
        with patch('app.core.config.settings', INVITATION_CODE_EXPIRE_TIME=7):
            with patch('random.choices', side_effect=[list("TESTCODE"), list("NEWCODE")]):
                # Generate invitation code
                invitation_code = invitation_code_utils.generate_invitation_code()
                
                # Verify a new non-duplicate code was generated
                assert invitation_code.code == "NEWCODE"
                
                # Verify both codes are saved
                saved_codes = invitation_code_utils._get_invitation_codes()
                assert len(saved_codes) == 2
                assert any(c.code == "TESTCODE" for c in saved_codes)
                assert any(c.code == "NEWCODE" for c in saved_codes)