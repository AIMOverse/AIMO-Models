from typing import List
import requests
from app.core.config import settings
from privy import AsyncPrivyAPI

class PrivyWalletUtils:
    """Handles Privy wallet authentication"""
    
    @staticmethod
    async def get_linked_solana_addresses(privy_id_token: str) -> List[str]:
        """
        Verify Privy ID token and verify wallet address
        
        Args:
            privy_id_token: Privy ID token
            
        Returns:
            dict: Contains user information
        """
        # Implementation required based on Privy's API documentation
        # Example implementation:
        app_id = settings.PRIVY_APP_ID
        app_secret = settings.PRIVY_APP_SECRET

        client = AsyncPrivyAPI(app_id=app_id, app_secret=app_secret)
        try:
            user = await client.users.get_by_id_token(id_token=privy_id_token)
            linked_accounts = user.linked_accounts
            solana_addresses = [account.address for account in linked_accounts if account.type == "wallet" and account.chain_type == "solana"]
            return solana_addresses
        except Exception as e:
            raise Exception(f"Failed to get linked solana addresses: {e}")
        

    @staticmethod
    async def verify_access_token(privy_auth_token: str) -> dict[str, str]:
        """
        Verify the Privy authentication token
        
        Args:
            privy_auth_token: Privy authentication token
            
        Returns:
            bool: True if the token is valid, False otherwise
        """
        app_id = settings.PRIVY_APP_ID
        app_secret = settings.PRIVY_APP_SECRET

        client = AsyncPrivyAPI(app_id=app_id, app_secret=app_secret)
        try:
            user = await client.users.verify_access_token(auth_token=privy_auth_token)
            return {
                "app_id": user["app_id"],
                "user_id": user["user_id"],
                "issuer": user["issuer"],
                "issued_at": user["issued_at"],
                "expiration": user["expiration"],
                "session_id": user["session_id"]
            }
        except Exception as e:
            raise Exception(f"Failed to verify auth token: {e}")
