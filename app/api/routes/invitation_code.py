from fastapi import APIRouter, Header

from app.core.config import settings
from app.exceptions.auth_exceptions import AuthException
from app.models.auth import GenerateInvitationCodeResponse, GetAvailableInvitationCodesResponse
from app.utils.invitation_code_utils import InvitationCodeUtils

router = APIRouter(prefix="", tags=["invitation_code"])

# Initialize Invitation Code Utility
invitation_code_utils = InvitationCodeUtils()


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
    invitation_code = invitation_code_utils.generate_invitation_code()  # Generate a new invitation code
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
    available_invitation_codes = invitation_code_utils.get_available_invitation_codes()  # Get all available invitation codes
    return GetAvailableInvitationCodesResponse(invitation_codes=available_invitation_codes)
