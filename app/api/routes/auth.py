import datetime

from fastapi import APIRouter, Depends, Form
from sqlmodel import Session

from app.core.db import engine
from app.entity.WalletAccount import WalletAccount
from app.entity.invitation_code import InvitationCode
from app.entity.EmailUser import EmailUser
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

    with Session(engine) as session:
        # Check if the wallet account exists
        wallet_account = session.get(WalletAccount, user_id)
            
        if wallet_account:
            # Update last login time
            wallet_account.last_login = datetime.datetime.now()
            session.commit()
            
            """
            Accounts need a valid invitation code to be created, so no need to check if the invitation code is valid
            """
            # # Check if the bound invitation code has expired
            # invitation_code = session.get(InvitationCode, wallet_account.invitation_code)
            # if not invitation_code or invitation_code.bound or invitation_code.expiration_time < datetime.datetime.now():
            #     raise AuthException(401, "Invalid invitation code")
            access_token = jwt_utils.generate_token({"wallet_address": user_id})
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
        # Check if the wallet already has a bound invitation code
        wallet_account = session.get(WalletAccount, data.privy_user_id)
        if wallet_account:
            raise AuthException(400, "Wallet already has a bound invitation code")
        
        # Check the validity of the invitation code
        invitation_code = session.get(InvitationCode, data.invitation_code)
        if not invitation_code or invitation_code.bound or invitation_code.expiration_time < datetime.datetime.now():
            raise AuthException(401, "Invalid invitation code")
        
        # Bind the invitation code to the wallet
        invitation_code.bound = True
        invitation_code.expiration_time = datetime.datetime.now() + datetime.timedelta(days=settings.BOUND_INVITATION_CODE_EXPIRE_TIME)

        wallet_account = WalletAccount(
            wallet_address=data.privy_user_id,
            invitation_code=data.invitation_code,
            created_at=datetime.datetime.now(),
            last_login=datetime.datetime.now()
        )
        
        session.add(invitation_code)
        session.add(wallet_account)
        session.commit()

    access_token = jwt_utils.generate_token({"wallet_address": data.privy_user_id})
        
    return BindInvitationCodeResponse(
        access_token=access_token
    )

@router.post("/email-login", response_model=EmailLoginResponse)
async def email_login(data: EmailLoginRequest) -> EmailLoginResponse:
    """
    Email login - generate invitation code and send via email
    
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
        
        # Generate unique invitation code
        invitation_code = generate_unique_invitation_code()
        
        # Save to database
        create_invitation_code_in_db(invitation_code, expiry_minutes)
        
        # Create or update email user record
        with Session(engine) as session:
            email_user = session.get(EmailUser, email)
            if email_user:
                # Update existing user
                email_user.invitation_code = invitation_code
                email_user.code_generated_at = datetime.datetime.now()
                email_user.code_expires_at = datetime.datetime.now() + datetime.timedelta(minutes=expiry_minutes)
                email_user.last_login = datetime.datetime.now()
            else:
                # Create new email user
                email_user = EmailUser(
                    email=email,
                    invitation_code=invitation_code,
                    code_generated_at=datetime.datetime.now(),
                    code_expires_at=datetime.datetime.now() + datetime.timedelta(minutes=expiry_minutes),
                    created_at=datetime.datetime.now(),
                    last_login=datetime.datetime.now()
                )
            
            session.add(email_user)
            session.commit()
        
        # Create subscriber in Listmonk if needed
        await listmonk_utils.create_subscriber_if_not_exists(email)
        
        # Send invitation code email
        email_sent = await listmonk_utils.send_invitation_code_email(
            recipient_email=email,
            invitation_code=invitation_code,
            expiry_minutes=expiry_minutes
        )
        
        if not email_sent:
            raise AuthException(500, "Failed to send invitation email")
        
        return EmailLoginResponse(
            success=True,
            message=f"Invitation code sent to {email}. Please check your email.",
            expires_in_minutes=expiry_minutes
        )
        
    except AuthException:
        raise
    except Exception as e:
        raise AuthException(500, f"An error occurred during email login: {str(e)}")


@router.post("/email-login-form", response_model=EmailLoginResponse)
async def email_login_form(emailAddress: str = Form(...)) -> EmailLoginResponse:
    """
    Email login via form data - generate invitation code and send via email
    
    Args:
        emailAddress (str): Email address from form data
        
    Returns:
        EmailLoginResponse: Response containing success status and message
    """
    # Create a request object to reuse existing logic
    email_request = EmailLoginRequest(emailAddress=emailAddress)
    return await email_login(email_request)
