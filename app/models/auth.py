from typing import List

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
