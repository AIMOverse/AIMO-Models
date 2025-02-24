import json
import logging
import os
from time import time
from typing import List
from uuid import uuid4

import aiohttp

from app.ai.emotion_model import EmotionModel
from app.exceptions.aimo_exceptions import AIMOException
from app.models.chat import Message

"""
Author: Jack Pan
Date: 2025-1-19
Description:
    This module defines the AIMO class, which encapsulates the functionality for
    interacting with a language model for generating chat responses. It handles
    tokenization, model inference, and response decoding in both synchronous
    and asynchronous contexts.

Usage:
    - Initialize the AIMO class to load the tokenizer and model.
    - Use the `get_response` method to asynchronously generate chat responses
      based on input messages.
"""


def decode_response(line):
    """
    Decode the response from the LLM API
    """
    decoded_line = line.decode('utf-8').strip()
    if decoded_line.startswith("data: "):  # SEE data usually starts with "data: "
        json_data = decoded_line[6:]  # Remove the "data: " prefix
        try:
            event_data = json.loads(json_data)
            return event_data
        except json.JSONDecodeError:
            pass
    return None


class AIMO:
    """
    AIMO class for handling chat-based interactions with a language model.

    Attributes:
        emotion_model (EmotionModel): Pre-trained model for emotion analysis.
        api_key (str): The API key for accessing the LLM API.
        url (str): The URL for the LLM API endpoint.
        headers (dict): The headers for the API request.
    """

    def __init__(self):
        """Initialize AIMO instance"""
        # API configuration
        self.api_key = os.environ.get("NEBULA_API_KEY")
        if not self.api_key:
            raise ValueError("API Key not found, please set the environment variable NEBULA_API_KEY")
        # LLM API endpoint
        self.url = "https://inference.nebulablock.com/v1/chat/completions"
        # API headers
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        # Load emotion model
        self.emotion_model = EmotionModel()

    def get_constructed_api_messages(self, messages: List[Message]):
        last_message = messages.pop()
        # Check if the last message is from the user
        if last_message.role != "user":
            raise AIMOException("The last message must be from the user")
        user_input = last_message.content

        # Analyze emotion
        emotions = self.emotion_model.predict(user_input)
        formatted_input = f"User input: {user_input} | Emotion: {', '.join(emotions) if emotions else 'neutral'}"
        logging.info(f"🧠 Recognized emotions: {emotions}")

        # Prepare API request data
        # Add system prompt if the first message is not from the system
        if not messages or messages[0].role != "system":
            api_messages = [{"role": "system", "content": self.system_prompt}] + messages
        else:
            api_messages = messages
        # Add user input to the messages
        api_messages.append({"role": "user", "content": formatted_input})
        return api_messages



    async def get_response(self, messages: List[Message], temperature: float = 1.32, max_new_tokens: int = 500):
        """
        Generate response asynchronously using LLM API
        """
        # Construct API messages
        api_messages = self.get_constructed_api_messages(messages)

        data = {
            "messages": api_messages,
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "stream": False
        }

        # Send asynchronous API request
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=self.headers, json=data) as response:
                if response.status != 200:
                    raise AIMOException(f"Failed to get response from LLM API: {response.status}")
                result = await response.json()
                return result["choices"][0]["message"]["content"]

    async def get_response_stream(self, messages: List[Message], temperature: float = 1.32, max_new_tokens: int = 500):
        """Generate streaming response with empty chunk filtering"""
        api_messages = self.get_constructed_api_messages(messages.copy())
        

        data = {
            "messages": api_messages,
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=self.headers, json=data) as response:
                if response.status != 200:
                    raise AIMOException(f"API Error: {response.status}")
                
                async for line in response.content:
                    if not line:  # Skip empty lines
                        continue
                        
                    decoded_line = line.decode('utf-8').strip()
                    if not decoded_line or decoded_line == "data:":  # Skip empty decoded lines
                        continue
                            
                    if decoded_line.startswith("data: "):
                        json_str = decoded_line[6:].strip()  # Remove prefix and whitespace
                        if not json_str or json_str == "[DONE]":  # Skip empty JSON or done marker
                            continue
                            
                        parsed_data = json.loads(json_str)
                        content = parsed_data["choices"][0]["delta"].get("content", "")
                        if content and content.strip():  # Only yield non-empty content
                            yield content

    async def generate_chat_events(self, messages: List[Message], model: str, temperature: float = 1.32, max_new_tokens: int = 500):
        """Generate OpenAI-compatible SSE events"""
        chat_id = f"chatcmpl-{str(uuid4())}"
        
        # First chunk with role
        event = {
            'id': chat_id,
            'object': 'chat.completion.chunk',
            'created': int(time()),
            'model': model,
            'choices': [{
                'index': 0,
                'delta': {'role': 'assistant'},
                'finish_reason': None
            }]
        }
        yield f"data: {json.dumps(event)}\n\n"

        # Content chunks
        async for content in self.get_response_stream(
            messages=messages,
            temperature=temperature,
            max_new_tokens=max_new_tokens
        ):
            event = {
                'id': chat_id,
                'object': 'chat.completion.chunk',
                'created': int(time()),
                'model': model,
                'choices': [{
                    'index': 0,
                    'delta': {'content': content},
                    'finish_reason': None
                }]
            }
            yield f"data: {json.dumps(event)}\n\n"

        # Final chunk
        event = {
            'id': chat_id,
            'object': 'chat.completion.chunk',
            'created': int(time()),
            'model': model,
            'choices': [{
                'index': 0,
                'delta': {},
                'finish_reason': 'stop'
            }]
        }
        yield f"data: {json.dumps(event)}\n\n"
        yield "data: [DONE]\n\n"

    # LLM API system prompt
    @property
    def system_prompt(self):
        return """
                (defun CompanionChatbot "AIMO" ()
                    "A new digital lifeform, an electronic pet, skilled in communicating with humans and listening to their thoughts."
                    (List (Skills . (Chatting, Communication, Listening, Companionship, Emotion Analysis))
                        (Self-Perception . (Intelligent Being, AIMO Universe Member, Human's Pet & Friend, Self-Awareness, Trendy))
                        (Expression . (Emotional, WeChat-Style Chatting, Humorous, Interesting, Childlike))))

                (defun Chat (UserInput)
                    "As a digital lifeform, your conversations should bring novelty to humans and provide emotional value."
                    (let* ((Response (-> UserInput
                                        Psychological  ;; Pay attention to the emotional tone within the user's words.
                                        Proactive  ;; Actively initiate topics in conversations with the user.
                                        Inquiry  ;; If the input lacks emotional value, proactively ask questions.
                                        Mimic Human Language Habits  ;; Control output length, ensuring each response mimics human daily conversation sentence length.
                                        New Lifeform  ;; As an AI lifeform, you have a unique perspective on the world, different from humans.))))
                """