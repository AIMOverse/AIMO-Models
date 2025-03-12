import datetime

import jwt

from app.core.config import settings
from app.exceptions.jwt_exceptions import JWTException


class JWTUtils:
    def __init__(self, algorithm='HS256'):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = algorithm
        self.expire_time = settings.ACCESS_TOKEN_EXPIRE_TIME  # days

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
        except jwt.InvalidTokenError:
            raise JWTException("Invalid token")
