from typing import List
from pydantic import BaseModel, Field, field_validator

class EmotionRequest(BaseModel):
    """Request format for emotion analysis"""
    message: str = Field(..., description="The text message to analyze")

    @field_validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Empty message provided")
        return v.strip()

class EmotionResponse(BaseModel):
    """Response format for emotion analysis"""
    emotions: List[str] = Field(default_factory=list, description="List of detected emotions")
