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
