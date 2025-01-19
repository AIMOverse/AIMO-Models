from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ai.aimo import AIMO
from server.dto import ChatDto
from server.vo import ChatItem

"""
Author: Jack Pan
Date: 2025-1-19
Description:
    This module implements a FastAPI server to provide a chat-based API endpoint.
    It integrates with the AIMO class to generate AI-powered responses based on user input.
    This is the controller of the server.
"""

# Initialize the FastAPI application
app = FastAPI()

# Initialize the AI model
aimo = AIMO()

# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/chat/")
async def generate(dto: ChatDto):
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
    return JSONResponse(content=ChatItem(role="assistant", content=response).model_dump())
