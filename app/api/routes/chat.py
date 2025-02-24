import json
from typing import Union
from uuid import uuid4
from time import time
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.ai.aimo import AIMO
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
    
    try:
        if not request.stream:
            # Non-streaming response
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
        else:
            # Streaming response
            async def event_generator():
                try:
                    # Send first chunk with role
                    first_chunk = {
                        "id": f"chatcmpl-{str(uuid4())}",
                        "object": "chat.completion.chunk",
                        "created": int(time()),
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {"role": "assistant"},
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(first_chunk)}\n\n"
                    
                    # Stream content chunks
                    async for chunk in aimo.get_response_stream(
                        messages=request.messages,
                        temperature=request.temperature,
                        max_new_tokens=request.max_tokens
                    ):
                        if chunk:
                            try:
                                content = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
                                if content.startswith('data: '):
                                    content = content[6:]  # Remove 'data: ' prefix
                                data = json.loads(content)
                                
                                chunk_data = {
                                    "id": f"chatcmpl-{str(uuid4())}",
                                    "object": "chat.completion.chunk",
                                    "created": int(time()),
                                    "model": request.model,
                                    "choices": [{
                                        "index": 0,
                                        "delta": {"content": data.get("content", "")},
                                        "finish_reason": None
                                    }]
                                }
                                yield f"data: {json.dumps(chunk_data)}\n\n"
                            except json.JSONDecodeError:
                                continue

                    # Send final chunk
                    final_chunk = {
                        "id": f"chatcmpl-{str(uuid4())}",
                        "object": "chat.completion.chunk",
                        "created": int(time()),
                        "model": request.model,
                        "choices": [{
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop"
                        }]
                    }
                    yield f"data: {json.dumps(final_chunk)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    print(f"Error in stream: {str(e)}")
                    raise

            return EventSourceResponse(event_generator())
            
    except Exception as e:
        print(f"Error in chat completion: {str(e)}")
        raise
