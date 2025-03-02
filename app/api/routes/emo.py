import logging
from fastapi import APIRouter, Depends
from app.models.openai import ChatCompletionRequest
from app.models.emotion import EmotionResponse
from app.ai.emotion_model import EmotionModel

"""
Author: Wesley Xu
Date: 2025-3-1
Description:
    This module defines the emotion analysis service endpoints
"""

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["emotion"])

# Initialize emotion model
emotion_model = EmotionModel()

@router.post("/analyze", response_model=EmotionResponse)
async def analyze_emotion(request: ChatCompletionRequest) -> EmotionResponse:
    """
    Analyze the emotional content of the input text.
    
    Args:
        request (ChatCompletionRequest): OpenAI-compatible request format
        
    Returns:
        EmotionResponse: Contains original text and detected emotions
    """
    # Get the last message from user as analysis target
    last_message = request.messages[-1]
    text = last_message.content
    
    # Perform emotion analysis
    emotions = emotion_model.predict(text, 0.2)
    logger.info(f"🎭 Analyzed emotions for text: {text[:50]}...")
    
    return EmotionResponse(
        text=text,
        emotions=emotions
    )
