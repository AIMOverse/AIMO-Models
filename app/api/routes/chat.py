from typing import Union

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

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
async def generate(dto: ChatDto) -> Union[Message, EventSourceResponse]:
    """
    Generate chat response
    """
    # Check if the stream flag is set
    if not dto.stream:
        # Generate a chat response
        response = await aimo.get_response(
            messages=dto.messages,
            temperature=dto.temperature,
            max_new_tokens=dto.max_new_tokens
        )
        result = Message(content=response, role="assistant")
        return result
    else:
        # Generate a chat response stream
        return EventSourceResponse(aimo.get_response_stream(dto.messages, dto.temperature, dto.max_new_tokens))
