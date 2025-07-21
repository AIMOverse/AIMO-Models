import datetime

from fastapi import APIRouter, Depends, Form
from sqlmodel import Session

from app.core.db import engine
from app.entity.User import User
from app.entity.invitation_code import InvitationCode
from app.services.user_service import UserService
from app.exceptions.auth_exceptions import AuthException
from app.models.auth import (
    BindInvitationCodeRequest, 
    BindInvitationCodeResponse, 
    CheckInvitationCodeRequest, 
    CheckInvitationCodeResponse, 
    WalletVerifyRequest, 
    WalletVerifyResponse,
    EmailLoginRequest,
    EmailLoginResponse
)
from app.utils.jwt_utils import JWTUtils
from app.utils.privy_wallet_utils import PrivyWalletUtils
from app.utils.listmonk_utils import listmonk_utils
from app.utils.invitation_code_utils import generate_unique_invitation_code, create_invitation_code_in_db
from app.core.config import settings  # Import settings from the configuration module

"""
Author: Jack Pan
Date: 2025-3-12
Description:
    This module defines the authentication service endpoints
"""

router = APIRouter(prefix="", tags=["auth"])

# Initialize JWTUtils
jwt_utils = JWTUtils()
privy_wallet_utils = PrivyWalletUtils()


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
        invitation_code.used = True
        session.add(invitation_code)
        session.commit()
        session.refresh(invitation_code)
    access_token = jwt_utils.generate_token({"InvitationCode": code})  # Generate a new access token
    return CheckInvitationCodeResponse(access_token=access_token)

@router.post("/wallet-verify", response_model=WalletVerifyResponse)
async def wallet_verify(data: WalletVerifyRequest) -> WalletVerifyResponse:
    """Verify wallet and return JWT token"""
    # Verify Privy authentication token
    try:
        user_claims = await PrivyWalletUtils.verify_access_token(data.privy_access_token)
    except Exception as e:
        raise AuthException(401, f"Invalid Privy authentication token")
    
    user_id = user_claims.get("user_id")
    if not user_id:
        raise AuthException(401, "user_id not found in Privy claims")

    # Check if user exists with this wallet address
    user = UserService.get_user_by_wallet(user_id)
    
    if user and user.can_login_with_wallet():
        # Update last login time
        UserService.update_last_login(user.user_id)
        
        access_token = jwt_utils.generate_token({"wallet_address": user_id, "user_id": user.user_id})
        return WalletVerifyResponse(
            user_id=user_id,
            access_token=access_token,
        )
    else:
        return WalletVerifyResponse(
            user_id=user_id,
            access_token=None,
        )
    
    # Generate JWT token containing the wallet address
    # access_token = jwt_utils.generate_token({"wallet_address": data.wallet_address})
        
    # return WalletVerifyResponse(
    #     access_token=access_token,
    #     is_new_user=is_new_user
    # )

@router.post("/bind-invitation-code", response_model=BindInvitationCodeResponse)
async def bind_invitation_code(
    data: BindInvitationCodeRequest
) -> BindInvitationCodeResponse:
    """Bind invitation code to wallet address"""
    with Session(engine) as session:
        # Check if user already exists with this wallet address
        existing_user = UserService.get_user_by_wallet(data.privy_user_id)
        if existing_user:
            raise AuthException(400, "Wallet already has a bound invitation code")
        
        # Check the validity of the invitation code
        invitation_code = session.get(InvitationCode, data.invitation_code)
        if not invitation_code or invitation_code.bound or invitation_code.expiration_time < datetime.datetime.now():
            raise AuthException(401, "Invalid invitation code")
        
        # Bind the invitation code to the wallet by creating a new user
        invitation_code.bound = True
        invitation_code.expiration_time = datetime.datetime.now() + datetime.timedelta(days=settings.BOUND_INVITATION_CODE_EXPIRE_TIME)
        
        # Create new user with wallet authentication
        user = UserService.create_user_with_wallet(
            wallet_address=data.privy_user_id,
            invitation_code=data.invitation_code
        )
        
        session.add(invitation_code)
        session.commit()

    access_token = jwt_utils.generate_token({"wallet_address": data.privy_user_id, "user_id": user.user_id})
        
    return BindInvitationCodeResponse(
        access_token=access_token
    )

@router.post("/email-login", response_model=EmailLoginResponse)
async def email_login(data: EmailLoginRequest) -> EmailLoginResponse:
    """
    Email login - generate verification code and send via email
    
    Args:
        data (EmailLoginRequest): Contains the email address
        
    Returns:
        EmailLoginResponse: Response containing success status and message
    """
    try:
        # Check Listmonk health first
        #if not await listmonk_utils.check_listmonk_health():
            #raise AuthException(503, "Email service is currently unavailable")
        
        email = data.email
        expiry_minutes = settings.EMAIL_LOGIN_EXPIRE_TIME
        
        # Generate unique verification code (using invitation code generator)
        verification_code = generate_unique_invitation_code()
        
        # Create or update user record
        user = UserService.get_user_by_email(email)
        if user:
            # Update existing user with verification code
            UserService.set_email_verification_code(
                user.user_id, 
                verification_code, 
                datetime.datetime.now() + datetime.timedelta(minutes=expiry_minutes)
            )
            UserService.update_last_login(user.user_id)
        else:
            # Create new user with email authentication
            user = UserService.create_user_with_email(email)
            UserService.set_email_verification_code(
                user.user_id,
                verification_code,
                datetime.datetime.now() + datetime.timedelta(minutes=expiry_minutes)
            )
        
        # Create subscriber in Listmonk if needed
        await listmonk_utils.create_subscriber_if_not_exists(email)
        
        # Send verification code email
        email_sent = await listmonk_utils.send_invitation_code_email(
            recipient_email=email,
            invitation_code=verification_code,
            expiry_minutes=expiry_minutes
        )
        
        if not email_sent:
            raise AuthException(500, "Failed to send verification email")
        
        return EmailLoginResponse(
            success=True,
            message=f"Verification code sent to {email}. Please check your email.",
            expires_in_minutes=expiry_minutes
        )
        
    except AuthException:
        raise
    except Exception as e:
        raise AuthException(500, f"An error occurred during email login: {str(e)}")


@router.post("/email-login-form", response_model=EmailLoginResponse)
async def email_login_form(emailAddress: str = Form(...)) -> EmailLoginResponse:
    """
    Email login via form data - generate verification code and send via email
    
    Args:
        emailAddress (str): Email address from form data
        
    Returns:
        EmailLoginResponse: Response containing success status and message
    """
    # Create a request object to reuse existing logic
    email_request = EmailLoginRequest(emailAddress=emailAddress)
    return await email_login(email_request)


@router.post("/email-verify")
async def email_verify(email: str = Form(...), verification_code: str = Form(...)):
    """
    Verify email with verification code and return JWT token
    
    Args:
        email (str): User email address
        verification_code (str): Verification code sent via email
        
    Returns:
        dict: Response containing access token if verification is successful
    """
    try:
        user = UserService.get_user_by_email(email)
        if not user:
            raise AuthException(404, "User not found")
        
        # Verify the email with the verification code
        if UserService.verify_email(user.user_id, verification_code):
            # Update last login
            UserService.update_last_login(user.user_id)
            
            # Generate JWT token
            access_token = jwt_utils.generate_token({"email": email, "user_id": user.user_id})
            
            return {
                "success": True,
                "access_token": access_token,
                "message": "Email verified successfully"
            }
        else:
            raise AuthException(401, "Invalid or expired verification code")
            
    except AuthException:
        raise
    except Exception as e:
        raise AuthException(500, f"An error occurred during email verification: {str(e)}")
