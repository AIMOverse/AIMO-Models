from typing import List, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class ChatDto(BaseModel):
    messages: List[Message]
    temperature: float = 1.32
    max_tokens: int = 500

class ChatItem(BaseModel):
    role: str = "assistant"
    content: str

class HealthCheck(BaseModel):
    status: str = "ok"