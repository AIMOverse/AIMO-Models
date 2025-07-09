import requests
import base64
from typing import Dict, Any, Optional
from app.core.config import settings
from app.utils.email_templates import EmailTemplates

"""
Author: Jack Pan
Date: 2025-7-9
Description:
    Listmonk utility class for sending emails
"""


class ListmonkUtils:
    """Utility class for interacting with Listmonk API"""
    
    def __init__(self):
        self.api_url = settings.LISTMONK_API_URL
        self.username = settings.LISTMONK_USERNAME
        self.password = settings.LISTMONK_PASSWORD
        self.default_sender_email = settings.DEFAULT_SENDER_EMAIL
        self.default_sender_name = settings.DEFAULT_SENDER_NAME
        
        # Create basic auth header
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
        expiry_minutes: int = 30
    ) -> bool:
        """
        Send invitation code email to recipient
        
        Args:
            recipient_email (str): Recipient's email address
            invitation_code (str): Generated invitation code
            expiry_minutes (int): Code expiry time in minutes
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Render email content
            html_content = EmailTemplates.render_invitation_email(
                invitation_code=invitation_code,
                expiry_minutes=expiry_minutes
            )
            
            plain_text_content = EmailTemplates.render_plain_text_email(
                invitation_code=invitation_code,
                expiry_minutes=expiry_minutes
            )
            
            # Prepare email data
            email_data = {
                "subscribers": [recipient_email],
                "template_id": None,  # We're sending custom content
                "subject": "🎉 Welcome to AIMO - Your Invitation Code Inside!",
                "body": html_content,
                "altbody": plain_text_content,
                "content_type": "html",
                "from_email": self.default_sender_email,
                "tags": ["invitation", "email-login"],
                "headers": [
                    {
                        "Reply-To": self.default_sender_email
                    }
                ]
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
            return response.status_code == 200
        except Exception as e:
            print(f"Listmonk health check failed: {str(e)}")
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
                timeout=10
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                if search_data.get("data", {}).get("results"):
                    # Subscriber exists
                    return search_data["data"]["results"][0]
            
            # Create new subscriber
            subscriber_data = {
                "email": email,
                "name": name or email.split("@")[0],
                "status": "enabled",
                "lists": [],  # Add to specific lists if needed
                "preconfirm_subscriptions": True
            }
            
            create_response = requests.post(
                f"{self.api_url}/api/subscribers",
                json=subscriber_data,
                headers=self.headers,
                timeout=10
            )
            
            if create_response.status_code == 200:
                return create_response.json().get("data")
            else:
                print(f"Failed to create subscriber. Status: {create_response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error managing subscriber: {str(e)}")
            return None


# Global instance
listmonk_utils = ListmonkUtils()
