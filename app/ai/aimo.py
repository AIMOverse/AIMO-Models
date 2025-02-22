import logging
import os

import aiohttp

from app.ai.emotion_model import EmotionModel
from app.exceptions.aimo_exceptions import AIMOException

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

    async def get_response(self, messages: list, temperature: float = 1.32, max_new_tokens: int = 500):
        """
        Generate response asynchronously using LLM API
        """

        # 1. Get the latest user input
        user_input = messages[-1].content

        # 2. Analyze emotion
        emotions = self.emotion_model.predict(user_input)
        formatted_input = f"User input: {user_input} | Emotion: {', '.join(emotions) if emotions else 'neutral'}"
        logging.info(f"🧠 Recognized emotions: {emotions}")

        # 3. Prepare API request data
        api_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": formatted_input}
        ]

        data = {
            "messages": api_messages,
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "stream": False
        }

        # 4. Send asynchronous API request
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=self.headers, json=data) as response:
                if response.status != 200:
                    raise AIMOException(f"Failed to get response from LLM API: {response.status}")
                result = await response.json()
                return result["choices"][0]["message"]["content"]

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