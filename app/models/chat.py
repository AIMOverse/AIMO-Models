from typing import List, Union

from pydantic import BaseModel, field_validator

"""
Author: Jack Pan
Date: 2025-1-19
Description:
    This module defines the models and structure of data used in chatting services
"""


class Message(BaseModel):
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
        messages (List[Message]): A list of chat messages, where each message contains a role and its content.
        temperature (float): A parameter controlling the randomness of the AI's response.
        max_new_tokens (int): The maximum number of tokens to generate in the AI's response.
    """
    messages: List[Message]
    temperature: Union[float, None]
    max_new_tokens: Union[int, None]
    stream: bool

    # Check if the length of the messages is more than 1

    @field_validator('messages')
    @classmethod
    def check_messages(cls, v):
        if len(v) < 1:
            raise ValueError('messages must contain at least one message')
        return v
