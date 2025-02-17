import os
import asyncio
import logging
import aiohttp
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
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
        """初始化 AIMO 实例"""
        # 设置设备
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 1. API 配置
        self.api_key = os.environ.get("NEBULA_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 API Key，请设置环境变量 NEBULA_API_KEY")
            
        self.url = "https://inference.nebulablock.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # DeepSeek API system prompt
        self.system_prompt = """ 
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
        
        # 2. 加载【情感分析模型】
        current_dir = Path(__file__).parent
        emotion_model_path = current_dir / "static" / "models" / "EmotionModule"
        logging.info(f"Loading emotion model from: {emotion_model_path}")
        
        if not emotion_model_path.exists():
            raise FileNotFoundError(f"情感模型目录不存在: {emotion_model_path}")
            
        self.emotion_model = EmotionModel(str(emotion_model_path), device=self.device)
        logging.info("Emotion model loaded.")

        '''
        # 3. 【本地对话模型】- 暂时注释，供未来使用
        chat_model_path = current_dir / "static" / "models" / "ChatModel"
        logging.info("Loading chat model...")
        self.chat_tokenizer = AutoTokenizer.from_pretrained(str(chat_model_path))
        self.chat_model = AutoModelForCausalLM.from_pretrained(
            str(chat_model_path),
            device_map="auto",
            torch_dtype=torch.float16
        ).to(self.device)
        logging.info("Chat model loaded.")
        '''

    async def get_response(self, messages: list, temperature: float = 1.32, max_new_tokens: int = 500):
        """
        使用 DeepSeek API 异步生成响应
        """
        if not messages:
            return "请输入有效的消息。"
            
        # 1. 获取用户最新的输入
        user_input = messages[-1].get("content", "")
        
        # 2. 分析情感
        emotions = self.emotion_model.predict(user_input)
        formatted_input = f"User input: {user_input} | Emotion: {', '.join(emotions) if emotions else 'neutral'}"
        logging.info(f"🧠 识别情绪: {emotions}")
        
        # 3. 准备 API 请求数据
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
        
        # 4. 发送异步 API 请求
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, headers=self.headers, json=data) as response:
                    result = await response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "❌ API 返回错误")
        except Exception as e:
            logging.error(f"API 请求失败: {str(e)}")
            return f"抱歉，发生了错误: {str(e)}"

    '''
    # 以下方法保留供未来使用本地模型
    async def _generate_text(self, inputs, temperature: float, max_new_tokens: int):
        """本地模型生成文本的异步方法"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._generate_sync,
            inputs,
            temperature,
            max_new_tokens
        )

    def _generate_sync(self, inputs, temperature: float, max_new_tokens: int):
        """本地模型生成文本的同步方法"""
        return self.chat_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=0.9,
        )
    '''
