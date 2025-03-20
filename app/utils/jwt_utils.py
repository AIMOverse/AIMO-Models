import datetime
import os
import uuid
from typing import Dict, Any, Optional

import jwt
from jwt.exceptions import PyJWTError

from app.exceptions.jwt_exceptions import JWTException

class JWTUtils:
    """JWT utility class for generating and validating JWT tokens"""
    
    def __init__(self, algorithm: str = 'HS256'):
        self.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
        self.algorithm = algorithm
        # Get expiration time from environment variable as integer
        self.expire_time = int(os.getenv("ACCESS_TOKEN_EXPIRE_TIME", "7"))
        # Default daily quota
        self.default_quota = int(os.getenv("DEFAULT_TOKEN_QUOTA", "1000"))
    
    def generate_token(self, payload: Dict[str, Any], custom_quota: Optional[int] = None) -> str:
        """
        Generate JWT token
        
        Args:
            payload: Data to be encoded
            custom_quota: Optional custom quota
            
        Returns:
            str: JWT token
        """
        expiration = datetime.datetime.now() + datetime.timedelta(days=self.expire_time)
        
        # Add necessary claims
        payload_copy = payload.copy()
        payload_copy.update({
            "exp": expiration,
            "jti": str(uuid.uuid4()),  # Add unique identifier
            "quota": custom_quota if custom_quota is not None else self.default_quota  # Add quota information
        })
        
        try:
            return jwt.encode(payload_copy, self.secret_key, algorithm=self.algorithm)
        except PyJWTError as e:
            raise JWTException(f"Token generation failed: {str(e)}")
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode JWT token
        
        Args:
            token: JWT token
            
        Returns:
            Dict[str, Any]: Decoded data
            
        Raises:
            JWTException: When token validation fails
        """
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise JWTException("Token expired")
        except PyJWTError:
            raise JWTException("Invalid token")
    
    def update_token_quota(self, token: str, new_quota: int) -> str:
        """
        Update token quota and return new token
        
        Args:
            token: Current JWT token
            new_quota: New quota value
            
        Returns:
            str: Updated JWT token
        """
        try:
            # Decode current token
            payload = self.decode_token(token)
            # Update quota
            return self.generate_token(payload, custom_quota=new_quota)
        except JWTException as e:
            raise JWTException(f"Failed to update token quota: {str(e)}")
