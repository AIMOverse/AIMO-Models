from typing import List
from pydantic import BaseModel, Field

from app.models.openai import ChatCompletionRequest

class EmotionRequest(BaseModel):
    """Request format for emotion analysis"""
    message: str = Field(..., description="The text message to analyze")

class EmotionResponse(BaseModel):
    """Response format for emotion analysis"""
    emotions: List[str] = Field(default_factory=list, description="List of detected emotions")
