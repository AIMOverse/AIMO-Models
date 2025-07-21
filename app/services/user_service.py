import uuid
import datetime
from typing import Optional
from sqlmodel import Session, select, or_
from app.entity.User import User
from app.core.db import engine

"""
Author: Jack Pan
Date: 2025-7-21
Description:
    User service for managing unified user authentication
"""


class UserService:
    """Service class for managing unified user authentication"""
    
    @staticmethod
    def create_user_with_email(email: str, invitation_code: Optional[str] = None) -> User:
        """Create a new user with email authentication"""
        with Session(engine) as session:
            user_id = str(uuid.uuid4())
            user = User(
                user_id=user_id,
                email=email,
                invitation_code=invitation_code
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    @staticmethod
    def create_user_with_wallet(wallet_address: str, invitation_code: Optional[str] = None) -> User:
        """Create a new user with wallet authentication"""
        with Session(engine) as session:
            user_id = str(uuid.uuid4())
            user = User(
                user_id=user_id,
                wallet_address=wallet_address,
                invitation_code=invitation_code
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    @staticmethod
    def create_user_with_both(email: str, wallet_address: str, invitation_code: Optional[str] = None) -> User:
        """Create a new user with both email and wallet authentication"""
        with Session(engine) as session:
            user_id = str(uuid.uuid4())
            user = User(
                user_id=user_id,
                email=email,
                wallet_address=wallet_address,
                invitation_code=invitation_code
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address"""
        with Session(engine) as session:
            statement = select(User).where(User.email == email)
            return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_wallet(wallet_address: str) -> Optional[User]:
        """Get user by wallet address"""
        with Session(engine) as session:
            statement = select(User).where(User.wallet_address == wallet_address)
            return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_login_identifier(identifier: str) -> Optional[User]:
        """Get user by either email or wallet address"""
        with Session(engine) as session:
            statement = select(User).where(
                or_(User.email == identifier, User.wallet_address == identifier)
            )
            return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by user ID"""
        with Session(engine) as session:
            statement = select(User).where(User.user_id == user_id)
            return session.exec(statement).first()
    
    @staticmethod
    def add_email_to_user(user_id: str, email: str) -> bool:
        """Add email to existing user"""
        with Session(engine) as session:
            # Check if email already exists
            existing_user = session.exec(select(User).where(User.email == email)).first()
            if existing_user:
                return False
            
            # Update user with email
            user = session.exec(select(User).where(User.user_id == user_id)).first()
            if user and not user.email:
                user.email = email
                session.add(user)
                session.commit()
                return True
            return False
    
    @staticmethod
    def add_wallet_to_user(user_id: str, wallet_address: str) -> bool:
        """Add wallet to existing user"""
        with Session(engine) as session:
            # Check if wallet already exists
            existing_user = session.exec(select(User).where(User.wallet_address == wallet_address)).first()
            if existing_user:
                return False
            
            # Update user with wallet
            user = session.exec(select(User).where(User.user_id == user_id)).first()
            if user and not user.wallet_address:
                user.wallet_address = wallet_address
                session.add(user)
                session.commit()
                return True
            return False
    
    @staticmethod
    def update_last_login(user_id: str) -> bool:
        """Update user's last login timestamp"""
        with Session(engine) as session:
            user = session.exec(select(User).where(User.user_id == user_id)).first()
            if user:
                user.last_login = datetime.datetime.now()
                session.add(user)
                session.commit()
                return True
            return False
    
    @staticmethod
    def set_email_verification_code(user_id: str, code: str, expires_at: datetime.datetime) -> bool:
        """Set email verification code for user"""
        with Session(engine) as session:
            user = session.exec(select(User).where(User.user_id == user_id)).first()
            if user and user.email:
                user.verification_code = code
                user.code_generated_at = datetime.datetime.now()
                user.code_expires_at = expires_at
                session.add(user)
                session.commit()
                return True
            return False
    
    @staticmethod
    def verify_email(user_id: str, code: str) -> bool:
        """Verify user's email with verification code"""
        with Session(engine) as session:
            user = session.exec(select(User).where(User.user_id == user_id)).first()
            if user and user.verification_code == code:
                # Check if code is not expired
                if user.code_expires_at and datetime.datetime.now() <= user.code_expires_at:
                    user.email_verified = True
                    user.verification_code = None  # Clear the code after verification
                    user.code_generated_at = None
                    user.code_expires_at = None
                    session.add(user)
                    session.commit()
                    return True
            return False
    
    @staticmethod
    def can_user_login(identifier: str) -> tuple[bool, Optional[User]]:
        """Check if user can login with given identifier and return user if possible"""
        user = UserService.get_user_by_login_identifier(identifier)
        if not user or not user.is_active:
            return False, None
        
        # Check if login method is valid
        if identifier == user.email:
            if user.can_login_with_email():
                return True, user
        elif identifier == user.wallet_address:
            if user.can_login_with_wallet():
                return True, user
        
        return False, None
    
    @staticmethod
    def deactivate_user(user_id: str) -> bool:
        """Deactivate a user"""
        with Session(engine) as session:
            user = session.exec(select(User).where(User.user_id == user_id)).first()
            if user:
                user.is_active = False
                session.add(user)
                session.commit()
                return True
            return False
    
    @staticmethod
    def activate_user(user_id: str) -> bool:
        """Activate a user"""
        with Session(engine) as session:
            user = session.exec(select(User).where(User.user_id == user_id)).first()
            if user:
                user.is_active = True
                session.add(user)
                session.commit()
                return True
            return False
