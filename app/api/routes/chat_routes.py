import logging
from fastapi import APIRouter

from app.ai.aimo import AIMO
from app.models.chat import ChatDto, Message
from app.models.health_check import HealthCheck

"""
Author: Jack Pan, Wesley Xu
Date: 2025-1-20
Description:
    This module defines the controller of chat services
"""
router = APIRouter(prefix="", tags=["chat"])

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the AI model
aimo = AIMO()

@router.post("/", response_model=Message)
async def generate(dto: ChatDto) -> Message:
    """
    Generate chat response
    """
    response = await aimo.get_response(
        messages=dto.messages,
        temperature=dto.temperature,
        max_new_tokens=dto.max_new_tokens
    )
    result = Message(content=response, role="assistant")
    return result

@router.get("/", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint
    """
    return HealthCheck(status="ok")