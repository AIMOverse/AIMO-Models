from typing import Any

from fastapi import APIRouter

from app.ai.aimo import AIMO
from app.models.chat import ChatDto, ChatItem


"""
Author: Jack Pan
Date: 2025-1-20
Description:
    This module defines the controller of chat services
"""
router = APIRouter(prefix="/chat", tags=["chat"])


# Initialize the AI model
aimo = AIMO()

@router.post("/", response_model=ChatItem)
async def generate(dto: ChatDto)->Any:
    """
    Handles POST requests to the /chat/ endpoint.

    This endpoint generates a response based on the input messages provided in the request body.
    It uses the AIMO class to process the input and generate a response.

    Args:
        dto (ChatDto): The request body containing messages, temperature, and max_new_tokens.

    Returns:
        JSONResponse: A JSON response containing the generated assistant message.
    """
    # Generate response using the AI model
    response = await aimo.get_response(dto.messages, dto.temperature, dto.max_new_tokens)

    # Return the response as a JSON object
    return ChatItem(role="assistant", content=response)