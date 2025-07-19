import requests
import base64
from typing import Dict, Any, Optional
from app.core.config import settings


"""
Author: Wesley Xu
Date: 2025-7-9
Description:
    Listmonk utility class for sending emails
"""


class ListmonkUtils:
    """Utility class for interacting with Listmonk API"""
    
    def __init__(self):
        self.api_url = settings.LISTMONK_API_URL
        # Use the working credentials from our tests
        self.username = "invitation_code_api"
        self.password = settings.LISTMONK_API_KEY  # Use API key as password
        self.default_sender_email = settings.DEFAULT_SENDER_EMAIL
        self.default_sender_name = settings.DEFAULT_SENDER_NAME
        # Default template ID for invitation emails (can be configured)
        self.default_invitation_template_id = getattr(settings, 'LISTMONK_INVITATION_TEMPLATE_ID', None)
        
        # Create auth header - use basic auth
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    
    async def send_invitation_code_email(
        self, 
        recipient_email: str, 
        invitation_code: str,
        expiry_minutes: int = 30,
        template_id: int = None
    ) -> bool:
        """
        Send invitation code email to recipient using Listmonk template
        
        Args:
            recipient_email (str): Recipient's email address
            invitation_code (str): Generated invitation code
            expiry_minutes (int): Code expiry time in minutes
            template_id (int): Listmonk template ID to use (optional)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # First, try to create/get subscriber
            subscriber = await self.create_subscriber_if_not_exists(recipient_email)
            
            # Prepare template data to be passed to Listmonk template
            template_data = {
                "invitation_code": invitation_code,
                "expiry_minutes": expiry_minutes
            }
            
            # If we have a subscriber, use their ID, otherwise use email directly
            if subscriber and subscriber.get('id'):
                # Prepare email data for transactional API with subscriber ID
                email_data = {
                    "subscriber_id": subscriber['id'],
                    "template_id": template_id or self.default_invitation_template_id,  # Use provided or default template
                    "data": template_data,  # Pass invitation code and expiry data to template
                    "messenger": "email"
                }
            else:
                # Fallback: try with subscriber emails (direct sending)
                email_data = {
                    "subscriber_emails": [recipient_email],
                    "template_id": template_id or self.default_invitation_template_id,  # Use provided or default template
                    "data": template_data,  # Pass invitation code and expiry data to template
                    "messenger": "email"
                }
            
            # Send email via Listmonk transactional API
            response = requests.post(
                f"{self.api_url}/api/tx",
                json=email_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return True
            else:
                # Log error for debugging (consider using proper logging in production)
                print(f"Failed to send email. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    async def check_listmonk_health(self) -> bool:
        """
        Check if Listmonk API is healthy
        
        Returns:
            bool: True if Listmonk is accessible, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/api/health",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Listmonk health check failed. Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Listmonk health check failed: {str(e)}")
            return False
    
    async def create_subscriber_if_not_exists(self, email: str, name: str = "") -> Optional[Dict[str, Any]]:
        """
        Create a subscriber in Listmonk if they don't exist
        
        Args:
            email (str): Subscriber email
            name (str): Subscriber name (optional)
            
        Returns:
            Dict[str, Any]: Subscriber data if successful, None otherwise
        """
        try:
            # Check if subscriber already exists
            search_response = requests.get(
                f"{self.api_url}/api/subscribers",
                params={"query": f"subscribers.email = '{email}'"},
                headers=self.headers,
                timeout=30
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                if search_data.get("data", {}).get("results"):
                    # Subscriber exists
                    return search_data["data"]["results"][0]
            
            # Try to create new subscriber with minimal data
            subscriber_data = {
                "email": email,
                "name": name or email.split("@")[0],
                "status": "enabled",
                "lists": [3],  # Add to list ID 3 (AIMO App Genesis) based on our earlier test
                "preconfirm_subscriptions": True
            }
            
            create_response = requests.post(
                f"{self.api_url}/api/subscribers",
                json=subscriber_data,
                headers=self.headers,
                timeout=30
            )
            
            if create_response.status_code == 200:
                return create_response.json().get("data")
            else:
                print(f"Could not create subscriber. Status: {create_response.status_code}")
                print(f"Response: {create_response.text}")
                return None
                
        except Exception as e:
            print(f"Error managing subscriber: {str(e)}")
            return None
    
    async def get_templates(self) -> Optional[Dict[str, Any]]:
        """
        Get all available templates from Listmonk
        
        Returns:
            Dict[str, Any]: Templates data if successful, None otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/api/templates",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get templates. Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting templates: {str(e)}")
            return None

    async def get_template_by_name(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific template by name
        
        Args:
            template_name (str): Name of the template to find
            
        Returns:
            Dict[str, Any]: Template data if found, None otherwise
        """
        try:
            templates_response = await self.get_templates()
            if templates_response and templates_response.get('data'):
                for template in templates_response['data']:
                    if template.get('name') == template_name:
                        return template
            return None
                
        except Exception as e:
            print(f"Error finding template by name: {str(e)}")
            return None

# Global instance
listmonk_utils = ListmonkUtils()
