import datetime
from fastapi import Request, FastAPI
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from app.exceptions.jwt_exceptions import JWTException
from app.utils.jwt_utils import JWTUtils
from app.entity.WalletAccount import WalletAccount
from app.entity.invitation_code import InvitationCode
from app.core.db import engine  # Adjusted import path for the database engine

class JWTMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: FastAPI, base_url: str, excluded_paths: list[str]):
        super().__init__(app)
        self.jwt_utils = JWTUtils()  # Initialize the JWT utility
        self.excluded_paths = excluded_paths  # List of paths to exclude from JWT validation
        self.base_url = base_url

    async def dispatch(self, request: Request, call_next):
            
        # Allow OPTIONS requests to pass through without authentication (for CORS preflight)
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response
        
        # Check if the request path is in excluded paths
        path = request.url.path.replace(self.base_url, "")
        if path in self.excluded_paths or request.method == "OPTIONS":
            # Proceed to the next middleware or route handler if the path is excluded
            response = await call_next(request)
            return response

        # Retrieve the Authorization header from the request
        authorization: str = request.headers.get('Authorization')
        # Extract the scheme (e.g., "Bearer") and the token from the header
        scheme, token = get_authorization_scheme_param(authorization)

        # Check if authorization header is missing or incorrect scheme
        if not authorization or scheme.lower() != 'bearer':
            return JSONResponse(
                status_code=401,
                content={"message": "Valid JWT Token is missing"}
            )

        try:
            # Attempt to decode and validate the JWT token
            payload = self.jwt_utils.decode_token(token)
            
            # Check if the token contains a wallet address
            wallet_address = payload.get("wallet_address")
            if wallet_address:
                # Verify if the wallet is registered with a valid invitation code
                with Session(engine) as session:
                    wallet_account = session.get(WalletAccount, wallet_address)
                    if not wallet_account:
                        return JSONResponse(
                            status_code=401,
                            content={"message": "Wallet not registered"}
                        )
                    
                    # Check if the bound invitation code is expired
                    invitation_code = session.get(InvitationCode, wallet_account.invitation_code)
                    if not invitation_code or invitation_code.expiration_time < datetime.datetime.now():
                        return JSONResponse(
                            status_code=401,
                            content={"message": "Bound invitation code has expired"}
                        )
            
            # Compatibility check for old invitation code tokens
            elif "InvitationCode" in payload:
                invitation_code = payload.get("InvitationCode")
                with Session(engine) as session:
                    code = session.get(InvitationCode, invitation_code)
                    if not code or code.expiration_time < datetime.datetime.now():
                        return JSONResponse(
                            status_code=401,
                            content={"message": "Invalid invitation code"}
                        )
                
        except JWTException as e:
            # If token validation fails, return an error response with details
            return JSONResponse(
                status_code=e.status_code,
                content={"message": e.message}
            )

        # Proceed to the next middleware or route handler if validation succeeds
        response = await call_next(request)
        return response