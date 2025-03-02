from typing import List
from pydantic import BaseModel, Field

from app.models.openai import ChatCompletionRequest

class EmotionResponse(BaseModel):
    """Response format for emotion analysis"""
    text: str = Field(..., description="The input text that was analyzed")
    emotions: List[str] = Field(default_factory=list, description="List of detected emotions")
