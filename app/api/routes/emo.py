import logging
from fastapi import APIRouter
from app.models.emotion import EmotionRequest, EmotionResponse
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
async def analyze_emotion(request: EmotionRequest) -> EmotionResponse:
    """
    Analyze the emotional content of the input text.
    
    Args:
        request (EmotionRequest): Simple message request format
        
    Returns:
        EmotionResponse: Contains original text and detected emotions
    """
    emotions = emotion_model.predict(request.message)
    logger.info(f"🎭 Analyzed emotions for text: {request.message[:50]}...")
    
    return EmotionResponse(emotions=emotions)
