from typing import List
from pydantic import BaseModel

"""
Author: Jack Pan
Date: 2025-1-19
Description:
    This module defines the structure of the JSON request body for the chat API endpoint.
    The structure is used to validate and parse the incoming JSON payload.
"""

class ChatDto(BaseModel):
    """
    Represents the structure of the JSON body for the chat API request.

    Attributes:
        messages (List[ChatItem]): A list of chat messages, where each message contains a role and its content.
        temperature (float): A parameter controlling the randomness of the AI's response.
        max_new_tokens (int): The maximum number of tokens to generate in the AI's response.
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

    messages: List[ChatItem]
    temperature: float
    max_new_tokens: int
