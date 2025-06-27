import datetime

from sqlmodel import SQLModel, Field

from app.core.config import settings


class InvitationCode(SQLModel, table=True):
    code: str = Field(primary_key=True,
                      unique=True,
                      index=True,  # Add index to the code field for faster query
                      description="Invitation code")
    expiration_time: datetime.datetime = Field(default=datetime.datetime.now() +
                                                       datetime.timedelta(days=settings.INVITATION_CODE_EXPIRE_TIME),
                                               description="Expiration time of the invitation code")
    used: bool = Field(default=False, description="Whether the invitation code has been used")

    bound: bool = Field(default=False, description="Whether the invitation code has been bound to a wallet")
