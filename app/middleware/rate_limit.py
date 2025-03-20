import datetime
import time
import logging
from typing import Callable, List, Optional, Dict, Any

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis.exceptions

from app.core.redis import RedisClient
from app.utils.jwt_utils import JWTUtils
from app.exceptions.jwt_exceptions import JWTException

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    JWT token rate limiting middleware
    """
    
    def __init__(
        self, 
        app: ASGIApp,
        jwt_utils: Optional[JWTUtils] = None,
        excluded_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.jwt_utils = jwt_utils or JWTUtils()
        self.excluded_paths = excluded_paths or ["/docs", "/redoc", "/openapi.json"]
        self.logger = logging.getLogger("rate_limit")
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and apply rate limiting
        """
        # Check if path is excluded
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Decode token
            payload = self.jwt_utils.decode_token(token)
            jti = payload.get("jti")
            quota = payload.get("quota", 1000)  # Default quota
            
            if not jti:
                return await call_next(request)
            
            # Check token usage rate
            rate_info = await self._check_rate_limit(jti, quota)
            
            # Add log records
            self.logger.info(
                f"Rate limit check - JTI: {jti[:8]}... Path: {request.url.path} "
                f"Usage: {rate_info['current']}/{quota} Remaining: {rate_info['remaining']}"
            )
            
            if rate_info["exceeded"]:
                self.logger.warning(f"Rate limit exceeded for token {jti[:8]}... on {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded. Try again tomorrow."}
                )
            
            # Execute request
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers["X-Rate-Limit-Limit"] = str(quota)
            response.headers["X-Rate-Limit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-Rate-Limit-Reset"] = str(rate_info["reset"])
            
            return response
            
        except JWTException:
            # JWT error, continue processing request
            return await call_next(request)
        except redis.exceptions.RedisError:
            # Redis error, allow request through but log error
            print("Redis connection error, skipping rate limit check")
            return await call_next(request)
        except Exception as e:
            # Unexpected error, log and allow request through
            print(f"Unexpected error in rate limit middleware: {str(e)}")
            return await call_next(request)
    
    async def _check_rate_limit(self, jti: str, quota: int) -> Dict[str, Any]:
        """
        Check and update token rate limit
        
        Args:
            jti: JWT ID
            quota: Quota limit
            
        Returns:
            Dict: Dictionary containing rate limit information
        """
        redis_client = RedisClient.get_client()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        key = f"rate_limit:{jti}:{today}"
        
        # Get today's usage count
        current_count = int(redis_client.get(key) or 0)
        
        # Check if quota is exceeded
        if current_count >= quota:
            # Calculate remaining time
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            reset_seconds = int((tomorrow - datetime.datetime.now()).total_seconds())
            
            return {
                "exceeded": True,
                "current": current_count,
                "remaining": 0,
                "reset": reset_seconds
            }
        
        # Increment usage count
        pipe = redis_client.pipeline()
        pipe.incr(key)
        
        # Set expiration time to ensure counter resets (if not already set)
        pipe.expire(key, 86400)  # 24 hours
        pipe.execute()
        
        # Updated count
        new_count = current_count + 1
        
        # Calculate reset time
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        reset_seconds = int((tomorrow - datetime.datetime.now()).total_seconds())
        
        return {
            "exceeded": False,
            "current": new_count,
            "remaining": quota - new_count,
            "reset": reset_seconds
        }
