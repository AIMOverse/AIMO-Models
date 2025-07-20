from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class CheckInvitationCodeRequest(BaseModel):
    """Request format for checking an invitation code"""
    invitation_code: str = Field(..., description="The invitation code to check")

    @field_validator('invitation_code')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Empty invitation code provided")
        if len(v) != 8:
            raise ValueError("Invalid invitation code length")
        return v.strip()


class CheckInvitationCodeResponse(BaseModel):
    """Response format for checking an invitation code"""
    access_token: str = Field(..., description="The access token")


class GenerateInvitationCodeResponse(BaseModel):
    """Response format for generating an invitation code"""
    invitation_code: str = Field(..., description="The generated invitation code")


class GetAvailableInvitationCodesResponse(BaseModel):
    """Response format for getting available invitation codes"""
    invitation_codes: List[str] = Field(..., description="The available invitation codes")


class WalletVerifyRequest(BaseModel):
    """Request format for verifying a wallet"""
    privy_access_token: str = Field(..., description="The Privy authentication token")


class WalletVerifyResponse(BaseModel):
    """Response format for verifying a wallet"""
    user_id: Optional[str] = Field(None, description="The user ID from Privy claims")
    access_token: Optional[str] = Field(None, description="If the user already bound an invitation code, return the access token")


class BindInvitationCodeRequest(BaseModel):
    """Request format for binding an invitation code"""
    privy_user_id: str = Field(..., description="The Privy user ID")
    invitation_code: str = Field(..., description="The invitation code to bind")


class BindInvitationCodeResponse(BaseModel):
    """Response format for binding an invitation code"""
    access_token: str = Field(..., description="Successfully bound invitation code, return the access token")

class EmailLoginRequest(BaseModel):
    """Request format for email login"""
    email: str = Field(..., description="User email address", alias="emailAddress")
    
    @field_validator('email')
    def validate_email(cls, v):
        if not v.strip():
            raise ValueError("Empty email address provided")
        # Basic email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v.strip()):
            raise ValueError("Invalid email format")
        return v.strip().lower()
    
    model_config = {"populate_by_name": True}


class EmailLoginResponse(BaseModel):
    """Response format for email login"""
    success: bool = Field(..., description="Whether the email was sent successfully")
    message: str = Field(..., description="Response message")
    expires_in_minutes: int = Field(..., description="Code expiry time in minutes")