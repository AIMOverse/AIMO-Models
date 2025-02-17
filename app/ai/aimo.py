import os
import logging
import aiohttp
import torch
from pathlib import Path
from app.ai.emotion_predictor import EmotionModel

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
        device (str): Specifies the device to use for model inference ('cuda' or 'cpu').
        emotion_model (EmotionModel): Pre-trained model for emotion analysis.
        api_key (str): The API key for accessing the LLM API.
        url (str): The URL for the LLM API endpoint.
        headers (dict): The headers for the API request.
    """

    def __init__(self):
        """Initialize AIMO instance"""
        # Set device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # 1. API configuration
        self.api_key = os.environ.get("NEBULA_API_KEY")
        if not self.api_key:
            raise ValueError("API Key not found, please set the environment variable NEBULA_API_KEY")

        self.url = "https://inference.nebulablock.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 2. Load emotion analysis model
        current_dir = Path(__file__).parent
        emotion_model_path = current_dir / "static" / "models" / "EmotionModule"
        logging.info(f"Loading emotion model from: {emotion_model_path}")

        if not emotion_model_path.exists():
            raise FileNotFoundError(f"Emotion model directory does not exist: {emotion_model_path}")

        self.emotion_model = EmotionModel()
        logging.info("Emotion model loaded.")

    async def get_response(self, messages: list, temperature: float = 1.32, max_new_tokens: int = 500):
        """
        Generate response asynchronously using LLM API
        """
        if not messages:
            return "Please enter a valid message."

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
                result = await response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "❌ API returned an error")

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