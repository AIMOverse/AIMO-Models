from typing import List, Union
from pydantic import BaseModel

"""
Author: Jack Pan
Date: 2025-1-19
Description:
    This module defines the models and structure of data used in chatting services
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

class ChatDto(BaseModel):
    """
    Represents the structure of the JSON body for the chat API request.

    Attributes:
        messages (List[ChatItem]): A list of chat messages, where each message contains a role and its content.
        temperature (float): A parameter controlling the randomness of the AI's response.
        max_new_tokens (int): The maximum number of tokens to generate in the AI's response.
    """
    messages: List[ChatItem]
    temperature: Union[float, None]
    max_new_tokens: Union[int, None]

class HealthCheck(BaseModel):
    status: str
