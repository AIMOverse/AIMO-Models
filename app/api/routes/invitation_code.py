import datetime
import random
import string

from fastapi import APIRouter, Header
from sqlmodel import select, Session

from app.core.config import settings
from app.core.db import engine
from app.entity.invitation_code import InvitationCode
from app.exceptions.auth_exceptions import AuthException
from app.models.auth import GenerateInvitationCodeResponse, GetAvailableInvitationCodesResponse

router = APIRouter(prefix="", tags=["invitation_code"])


@router.post("/generate-invitation-code", response_model=GenerateInvitationCodeResponse)
async def generate_invitation_code(api_key: str = Header(...)) -> GenerateInvitationCodeResponse:
    """
    Generate a new invitation code

    Args:
        api_key (str): The API key to authenticate

    Returns:
        GenerateInvitationCodeResponse: Contains InvitationCode
    """
    # Check if the API key is valid
    if api_key != settings.ADMIN_API_KEY:
        raise AuthException(status_code=401, message="Invalid APIKEY")
    with Session(engine) as session:
        statement = select(InvitationCode)  # Get all the existing invitation codes
        existing_invitation_codes = session.exec(statement)

        code_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Generate a random code
        while any([code.code == code_str for code in existing_invitation_codes]):  # Check if the code is already used
            code_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Generate a new random code
        expiration_time = datetime.datetime.now() + datetime.timedelta(
            days=settings.INVITATION_CODE_EXPIRE_TIME)  # Calculate the expiration time
        invitation_code = InvitationCode(code=code_str, expiration_time=expiration_time,
                                         used=False, bound=False)  # Create a new invitation code object
        # Add the new invitation code to the database
        session.add(invitation_code)
        session.commit()
        session.refresh(invitation_code)
    return GenerateInvitationCodeResponse(invitation_code=invitation_code.code)


@router.get("/get-available-invitation-codes", response_model=GetAvailableInvitationCodesResponse)
async def get_available_invitation_codes(api_key: str = Header(...)) -> GetAvailableInvitationCodesResponse:
    """
    Get all available invitation codes

    Args:
        api_key (str): The API key to authenticate

    Returns:
        GetAvailableInvitationCodesResponse: Contains Available InvitationCodes
    """
    # Check if the API key is valid
    if api_key != settings.ADMIN_API_KEY:
        raise AuthException(status_code=401, message="Invalid APIKEY")
    # Get all the existing invitation codes
    with Session(engine) as session:
        statement = select(InvitationCode).where(not InvitationCode.used
                                                 and InvitationCode.expiration_time > datetime.datetime.now())
        available_invitation_codes = session.exec(statement).all()

    return GetAvailableInvitationCodesResponse(invitation_codes=[code.code for code in available_invitation_codes])
