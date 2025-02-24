import json
import logging
from typing import Union
from typing import AsyncGenerator
from uuid import uuid4
from time import time
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.ai.aimo import AIMO

logger = logging.getLogger(__name__)
from app.models.openai import (
    ChatCompletionRequest, 
    ChatCompletionResponse,
    ChatChoice,
    Message
)

"""
Author: Jack Pan, Wesley Xu
Date: 2025-1-20
Description:
    OpenAI-compatible chat completion API controller
"""

router = APIRouter(tags=["chat"])
aimo = AIMO()

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest) -> Union[ChatCompletionResponse, EventSourceResponse]:
    """OpenAI-compatible chat completion endpoint"""
    if not request.stream:
        response = await aimo.get_response(
            messages=request.messages,
            temperature=request.temperature,
            max_new_tokens=request.max_tokens
        )
        
        return ChatCompletionResponse(
            model=request.model,
            choices=[
                ChatChoice(
                    index=0,
                    message=Message(role="assistant", content=response),
                    finish_reason="stop"
                )
            ]
        )

    return EventSourceResponse(
        aimo.generate_chat_events(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_new_tokens=request.max_tokens
        )
    )
