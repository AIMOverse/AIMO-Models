import datetime
import os
import uuid

import jwt

from app.exceptions.jwt_exceptions import JWTException


class JWTUtils:
    """JWT Utility for token generation and validation"""
    
    def __init__(self, algorithm='HS256'):
        """Initialize JWT utils with configuration"""
        self.secret_key = os.environ.get("SECRET_KEY")
        self.algorithm = algorithm
        self.expire_time = int(os.environ.get("ACCESS_TOKEN_EXPIRE_TIME", 7))
        self.max_chat_count = int(os.environ.get("MAX_CHAT_COUNT", 1000))
        
    def generate_token(self, payload):
        """Generate JWT token with conversation count tracking"""
        payload_copy = payload.copy()
        token_id = str(uuid.uuid4())
        
        # Add expiration time
        payload_copy['exp'] = datetime.datetime.now() + datetime.timedelta(days=self.expire_time)
        
        # Add unique ID, conversation count limit, and current conversation count
        payload_copy['jti'] = token_id
        payload_copy['max_chat_count'] = self.max_chat_count
        payload_copy['chat_count'] = 0
        payload_copy['issued_at'] = datetime.datetime.now().timestamp()
        
        token = jwt.encode(payload_copy, self.secret_key, algorithm=self.algorithm)
        return token
        
    def decode_token(self, token):
        """Decode and parse JWT token"""
        try:
            decoded = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return decoded
        except jwt.ExpiredSignatureError:
            raise JWTException("Token expired")
        except jwt.InvalidTokenError:
            raise JWTException("Invalid token")
            
    def increment_chat_count(self, token):
        """
        Increment the conversation count in the token and return the updated token.
        If the maximum limit is reached, raise an exception.
        """
        try:
            # Decode the current token
            decoded = self.decode_token(token)
            
            # Get the current conversation count
            current_count = decoded.get('chat_count', 0)
            max_count = decoded.get('max_chat_count', self.max_chat_count)
            
            # Check if the limit is exceeded
            if current_count >= max_count:
                raise JWTException("Token chat limit exceeded")
            
            # Increment the count
            decoded['chat_count'] = current_count + 1
            
            # Re-encode the token
            updated_token = jwt.encode(decoded, self.secret_key, algorithm=self.algorithm)
            
            return updated_token, decoded['chat_count']
        except Exception as e:
            raise JWTException(f"Failed to update token: {str(e)}")
        