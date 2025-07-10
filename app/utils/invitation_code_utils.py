import datetime
import random
import string
from sqlmodel import select, Session
from app.core.db import engine
from app.entity.invitation_code import InvitationCode
from app.core.config import settings

"""
Author: Jack Pan
Date: 2025-7-9
Description:
    Invitation code generation utilities
"""


def generate_unique_invitation_code() -> str:
    """
    Generate a unique 8-character invitation code
    
    Returns:
        str: Unique invitation code
    """
    with Session(engine) as session:
        statement = select(InvitationCode)
        existing_invitation_codes = session.exec(statement)
        existing_codes = {code.code for code in existing_invitation_codes}
        
        # Generate a unique code
        while True:
            code_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            if code_str not in existing_codes:
                return code_str


def create_invitation_code_in_db(code: str, expire_minutes: int = None) -> InvitationCode:
    """
    Create and save an invitation code to the database
    
    Args:
        code (str): The invitation code
        expire_minutes (int): Expiry time in minutes (default uses settings)
        
    Returns:
        InvitationCode: The created invitation code object
    """
    if expire_minutes is None:
        expire_minutes = settings.EMAIL_LOGIN_EXPIRE_TIME
        
    expiration_time = datetime.datetime.now() + datetime.timedelta(minutes=expire_minutes)
    
    invitation_code = InvitationCode(
        code=code,
        expiration_time=expiration_time,
        used=False,
        bound=False
    )
    
    with Session(engine) as session:
        session.add(invitation_code)
        session.commit()
        session.refresh(invitation_code)
    
    return invitation_code
