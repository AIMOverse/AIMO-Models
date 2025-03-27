import logging
from fastapi import Request, FastAPI
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.exceptions.jwt_exceptions import JWTException
from app.utils.jwt_utils import JWTUtils

logger = logging.getLogger(__name__)

class ChatLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit the number of user conversations.
    Only applies to chat and emotion analysis endpoints.
    """

    def __init__(self, app: FastAPI, base_url: str):
        super().__init__(app)
        self.jwt_utils = JWTUtils()
        self.base_url = base_url
        # List of endpoints requiring conversation count tracking
        self.chat_endpoints = [
            f"{base_url}/chat/completions",
            f"{base_url}/emotion/analyze"
        ]

    async def dispatch(self, request: Request, call_next):
        # Check if the request is related to chat
        if request.url.path not in self.chat_endpoints:
            # If not a chat request, allow it to proceed
            response = await call_next(request)
            return response

        # Get Authorization from request headers
        authorization: str = request.headers.get('Authorization')
        if not authorization:
            return JSONResponse(
                status_code=401,
                content={"message": "Authorization header is missing"}
            )

        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() != 'bearer':
            return JSONResponse(
                status_code=401,
                content={"message": "Invalid authorization scheme"}
            )

        try:
            # Increment conversation count and get the updated token
            updated_token, current_count = self.jwt_utils.increment_chat_count(token)
            
            # Process the request
            response = await call_next(request)
            
            # Add the updated token to the response headers
            response.headers["X-Updated-Token"] = updated_token
            response.headers["X-Chat-Count"] = str(current_count)
            
            return response
            
        except JWTException as e:
            if "chat limit exceeded" in str(e):
                # If conversation limit is exceeded, return a 429 status code
                return JSONResponse(
                    status_code=429,
                    content={"message": "Chat limit exceeded for this invitation code. Please use a new invitation code."}
                )
            else:
                # Other JWT-related errors, return a 401 status code
                logger.error(f"JWT error: {str(e)}")
                return JSONResponse(
                    status_code=401,
                    content={"message": str(e)}
                )
        except Exception as e:
            # Other errors
            logger.error(f"Error in chat limit middleware: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"message": "Internal server error"}
            )