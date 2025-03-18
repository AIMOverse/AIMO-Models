import datetime

from fastapi import APIRouter
from sqlmodel import Session

from app.core.db import engine
from app.entity.invitation_code import InvitationCode
from app.exceptions.auth_exceptions import AuthException
from app.models.auth import CheckInvitationCodeRequest, CheckInvitationCodeResponse
from app.utils.jwt_utils import JWTUtils

"""
Author: Jack Pan
Date: 2025-3-12
Description:
    This module defines the authentication service endpoints
"""

router = APIRouter(prefix="", tags=["auth"])

# Initialize JWTUtils
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
    with Session(engine) as session:
        invitation_code = session.get(InvitationCode, code)  # Get the invitation code from the database
        if not invitation_code or invitation_code.used or invitation_code.expiration_time < datetime.datetime.now():
            raise AuthException(401, "Invalid invitation code")
    access_token = jwt_utils.generate_token({"InvitationCode": code})  # Generate a new access token
    return CheckInvitationCodeResponse(access_token=access_token)



