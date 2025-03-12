from fastapi import APIRouter

from app.exceptions.auth_exceptions import AuthException
from app.models.auth import CheckInvitationCodeRequest, CheckInvitationCodeResponse
from app.utils.invitation_code_utils import InvitationCodeUtils
from app.utils.jwt_utils import JWTUtils

"""
Author: Jack Pan
Date: 2025-3-12
Description:
    This module defines the authentication service endpoints
"""

router = APIRouter(prefix="", tags=["auth"])

# Initialize Invitation Code Utility
invitation_code_utils = InvitationCodeUtils()
jwt_utils = JWTUtils()


@router.post("/check-invitation-code", response_model=CheckInvitationCodeResponse)
async def check_invitation_code(data: CheckInvitationCodeRequest) -> CheckInvitationCodeResponse:
    """
    Check if the invitation code is valid and return an access token

    Args:
        data (CheckInvitationCodeRequest):  Contains the invitation code to check

    Returns:
        CheckInvitationCodeResponse: Contains access token
    """
    code = data.invitation_code  # Get the invitation code from the request
    is_valid = invitation_code_utils.check_invitation_code(code)  # Check if the code is valid
    if not is_valid:
        raise AuthException(401, "Invalid invitation code")
    access_token = jwt_utils.generate_token({"InvitationCode": code})  # Generate a new access token
    return CheckInvitationCodeResponse(access_token=access_token)



