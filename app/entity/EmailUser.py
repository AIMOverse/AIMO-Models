import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

"""
Author: Jack Pan
Date: 2025-7-9
Description:
    Email user entity for email-based authentication
"""


class EmailUser(SQLModel, table=True):
    """Email user entity"""
    __tablename__ = "email_users"
    
    email: str = Field(primary_key=True, description="User email address")
    invitation_code: Optional[str] = Field(default=None, description="Generated invitation code")
    code_generated_at: Optional[datetime.datetime] = Field(default=None, description="Code generation timestamp")
    code_expires_at: Optional[datetime.datetime] = Field(default=None, description="Code expiration timestamp")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Account creation timestamp")
    last_login: Optional[datetime.datetime] = Field(default=None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Whether the user is active")
