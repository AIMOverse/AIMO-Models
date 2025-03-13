import os
import datetime
import jwt  # 确保这里导入了PyJWT
from app.exceptions.jwt_exceptions import JWTException

class JWTUtils:
    """JWT Utility for token generation and validation"""
    
    def __init__(self, algorithm='HS256'):
        """Initialize JWT utils with configuration"""
        self.secret_key = os.environ.get("SECRET_KEY")
        self.algorithm = algorithm
        self.expire_time = int(os.environ.get("ACCESS_TOKEN_EXPIRE_TIME", 7))
        
    def generate_token(self, payload):
        """Generate JWT token"""
        payload_copy = payload.copy()
        payload_copy['exp'] = datetime.datetime.now() + datetime.timedelta(days=self.expire_time)
        token = jwt.encode(payload_copy, self.secret_key, algorithm=self.algorithm)
        return token
        
    def decode_token(self, token):
        """Decode and parse JWT token"""
        try:
            decoded = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return decoded
        except jwt.ExpiredSignatureError:
            raise JWTException("Token expired")
        except Exception:
            raise JWTException("Invalid token")
