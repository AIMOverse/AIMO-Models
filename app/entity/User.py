import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from app.entity.invitation_code import InvitationCode

"""
Author: Wesley Xu
Date: 2025-7-21
Description:
    Unified user entity that supports both email and wallet authentication
"""


class User(SQLModel, table=True):
    daily_token_limit: int = Field(default=10000, description="Daily token usage limit")
    daily_token_used: int = Field(default=0, description="Tokens used today")
    token_limit_refresh_at: Optional[datetime.datetime] = Field(default=None, description="Next refresh time for token limit")
    """Unified user entity that supports both email and wallet authentication"""
    __tablename__ = "users"
    
    user_id: str = Field(primary_key=True, description="Unique user identifier")
    email: Optional[str] = Field(default=None, unique=True, index=True, description="User email address")
    wallet_address: Optional[str] = Field(default=None, unique=True, index=True, description="Wallet address")
    invitation_code: Optional[str] = Field(foreign_key="invitationcode.code", default=None, description="Bound invitation code")
    
    # Email verification fields
    verification_code: Optional[str] = Field(default=None, description="Email verification code")
    code_generated_at: Optional[datetime.datetime] = Field(default=None, description="Code generation timestamp")
    code_expires_at: Optional[datetime.datetime] = Field(default=None, description="Code expiration timestamp")
    email_verified: bool = Field(default=False, description="Whether email is verified")
    
    # Common user fields
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Account creation timestamp")
    last_login: Optional[datetime.datetime] = Field(default=None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Whether the user is active")
    
    # Relationship
    invitation: Optional[InvitationCode] = Relationship()
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure at least one authentication method is provided
        if not self.email and not self.wallet_address:
            raise ValueError("User must have either email or wallet_address")
    
    @property
    def login_methods(self) -> list[str]:
        """Get available login methods for this user"""
        methods = []
        if self.email:
            methods.append("email")
        if self.wallet_address:
            methods.append("wallet")
        return methods
    
    def can_login_with_email(self) -> bool:
        """Check if user can login with email"""
        return self.email is not None and self.email_verified
    
    def can_login_with_wallet(self) -> bool:
        """Check if user can login with wallet"""
        return self.wallet_address is not None
    
    def has_both_auth_methods(self) -> bool:
        """Check if user has both email and wallet authentication"""
        return self.email is not None and self.wallet_address is not None
