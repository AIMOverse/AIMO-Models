from pydantic import BaseModel

"""
Author: Jack Pan
Date: 2025-1-19
Description:
    This module defines the structure of the JSON body for responses.
    The structure is used to return the JSON response from the server.
"""

class ChatItem(BaseModel):
    """
    Represents an individual chat message.

    Attributes:
        role (str): The role of the message sender, e.g., 'user' or 'assistant'.
        content (str): The content of the chat message.
    """
    role: str
    content: str
