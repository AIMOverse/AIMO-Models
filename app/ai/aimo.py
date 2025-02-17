# aimo.py
import asyncio
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from emotion_predictor import EmotionModel

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

# logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class AIMO:
    """
    AIMO class for handling chat-based interactions with a language model.

    Attributes:
        device (str): Specifies the device to use for model inference ('cuda' or 'cpu').
        chat_tokenizer (AutoTokenizer): Tokenizer for processing input and output text.
        chat_model (AutoModelForCausalLM): Pre-trained language model for text generation.
        emotion_model (EmotionModel): Pre-trained model for emotion analysis.
    """

    def __init__(self):
        # 选择设备（GPU 优先）
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # 1. 加载【对话生成模型】(本地)
        #    目前你暂时使用第三方 API 进行对话生成，可先保留以下代码以备后续切换。
        '''
        chat_model_path = "static/models/ChatModel"
        logging.info("Loading chat tokenizer and model (local usage, if needed)...")
        self.chat_tokenizer = AutoTokenizer.from_pretrained(chat_model_path)
        self.chat_model = AutoModelForCausalLM.from_pretrained(chat_model_path).to(self.device)
        logging.info("Chat tokenizer and model loaded (local usage).")
        '''

        # 2. 加载【情感分析模型】
        emotion_model_path = "static/models/EmotionModel"
        logging.info("Loading emotion model...")
        self.emotion_model = EmotionModel(emotion_model_path, device=self.device)
        logging.info("Emotion model loaded.")

    async def get_response(self, messages: list, temperature: float = 0.6, max_new_tokens: int = 100):
        """
        Asynchronously generates a response from the locally loaded language model.

        NOTE:
            - This method is currently unused if you rely on外部API进行对话生成。
            - 保留该方法以便后续切换到本地模型时，直接启用即可。

        Args:
            messages (list): A list of dictionaries containing the chat history.
                Each dictionary should have 'role' and 'content' keys.
            temperature (float, optional): Controls the randomness of the response. Defaults to 0.6.
            max_new_tokens (int, optional): The maximum number of tokens to generate. Defaults to 100.

        Returns:
            str: The generated response as a string.
        """
        # 这里要用 self.chat_tokenizer 而不是 self.tokenizer
        inputs = self.chat_tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.device)

        # 异步调用生成
        outputs = await self._generate_text(inputs, temperature=temperature, max_new_tokens=max_new_tokens)

        # 截取并解码
        # 假设 outputs[0] 是生成的 token 列表
        response_tokens = outputs[0][inputs.shape[-1]:]
        return self.chat_tokenizer.decode(response_tokens, skip_special_tokens=True)

    async def _generate_text(self, inputs, temperature: float, max_new_tokens: int):
        """
        Runs the text generation process asynchronously using a thread pool executor.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._generate_sync,
            inputs,
            temperature,
            max_new_tokens
        )

    def _generate_sync(self, inputs, temperature: float, max_new_tokens: int):
        """
        Synchronously generates text using the locally loaded model.
        """
        # 注意这里要用 self.chat_model 而不是 self.model
        return self.chat_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=0.9,
        )
