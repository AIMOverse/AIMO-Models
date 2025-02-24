from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
from time import time
from uuid import uuid4

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    """OpenAI Chat Completion Request Format"""
    model: str = Field(default="aimo-chat")
    messages: List[Message]
    temperature: Optional[float] = 1.32
    top_p: Optional[float] = 0.9
    n: Optional[int] = 1
    stream: Optional[bool] = False
    max_tokens: Optional[int] = 500  # This will be mapped to max_new_tokens internally
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

class ChatChoice(BaseModel):
    index: int
    message: Optional[Message] = None
    delta: Optional[Dict] = None
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    """OpenAI Chat Completion Response Format"""
    id: str = Field(default_factory=lambda: f"chatcmpl-{str(uuid4())}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time()))
    model: str
    choices: List[ChatChoice]
    usage: Optional[Dict] = Field(default_factory=lambda: {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    })
