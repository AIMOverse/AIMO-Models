from fastapi import APIRouter

from app.ai.aimo import AIMO
from app.models.chat import ChatDto, Message

"""
Author: Jack Pan, Wesley Xu
Date: 2025-1-20
Description:
    This module defines the controller of chat services
"""
router = APIRouter(prefix="", tags=["chat"])

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