from fastapi import Depends, HTTPException
from fastapi import security
from fastapi.security import HTTPAuthorizationCredentials
import requests
from app.core.config import settings
from app.utils.jwt_utils import JWTUtils

class PrivyWalletUtils:
    """Handles Privy wallet authentication"""
    
    @staticmethod
    async def verify_auth_token(auth_token: str) -> dict:
        """
        Verify Privy authentication token and retrieve wallet address
        
        Args:
            auth_token: Privy authentication token
            
        Returns:
            dict: Contains user information and wallet address
        """
        # Implementation required based on Privy's API documentation
        # Example implementation:
        headers = {
            "Authorization": f"Bearer {settings.PRIVY_API_KEY}"
        }
        
        response = requests.get(
            f"{settings.PRIVY_API_BASE}/auth/verify",
            headers=headers,
            params={"token": auth_token}
        )
        
        if response.status_code != 200:
            raise Exception("Invalid Privy auth token")
            
        data = response.json()
        return data