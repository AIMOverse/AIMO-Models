import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.entity.invitation_code import InvitationCode

class WalletAccount(SQLModel, table=True):
    wallet_address: str = Field(primary_key=True, 
                               unique=True, 
                               index=True,
                               description="Wallet address")
    invitation_code: str = Field(foreign_key="invitationcode.code", 
                                description="Bound invitation code")
    created_at: datetime.datetime = Field(default=datetime.datetime.now(),
                                         description="Account creation time")
    last_login: datetime.datetime = Field(default=datetime.datetime.now(),
                                         description="Last login time")
    
    invitation: InvitationCode = Relationship()