import asyncio
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

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
        tokenizer (AutoTokenizer): Tokenizer for processing input and output text.
        model (AutoModelForCausalLM): The pre-trained language model for text generation.

    Methods:
        get_response(messages, temperature, max_new_tokens):
            Asynchronously generates a response based on the input messages.
    """
    def __init__(self):
        """
        Initializes the AIMO class by loading the tokenizer and the model.
        The model is loaded onto the appropriate device ('cuda' or 'cpu').
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_path = "OEvortex/HelpingAI2.5-2B"
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        # Load Model
        self.model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)

    async def get_response(self, messages: list, temperature: float = 0.6, max_new_tokens: int = 100):
        """
        Asynchronously generates a response from the language model.

        Args:
            messages (list): A list of dictionaries containing the chat history.
                Each dictionary should have 'role' and 'content' keys.
            temperature (float, optional): Controls the randomness of the response. Defaults to 0.6.
            max_new_tokens (int, optional): The maximum number of tokens to generate. Defaults to 100.

        Returns:
            str: The generated response as a string.
        """
        # Tokenize the input (synchronous operation)
        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.device)

        # Asynchronously generate text
        outputs = await self._generate_text(inputs, temperature=temperature, max_new_tokens=max_new_tokens)

        # Decode the output (synchronous operation)
        response = outputs[0][inputs.shape[-1]:]
        return self.tokenizer.decode(response, skip_special_tokens=True)

    async def _generate_text(self, inputs, temperature: float, max_new_tokens: int):
        """
        Runs the text generation process asynchronously using a thread pool executor.

        Args:
            inputs: The tokenized input data.
            temperature (float): Controls the randomness of the response.
            max_new_tokens (int): The maximum number of tokens to generate.

        Returns:
            torch.Tensor: The generated token tensor.
        """
        # Run model generation in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate_sync, inputs, temperature, max_new_tokens)

    def _generate_sync(self, inputs, temperature: float, max_new_tokens: int):
        """
        Synchronously generates text using the model.

        Args:
            inputs: The tokenized input data.
            temperature (float): Controls the randomness of the response.
            max_new_tokens (int): The maximum number of tokens to generate.

        Returns:
            torch.Tensor: The generated token tensor.
        """
        return self.model.generate(
            inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=0.9,
        )
