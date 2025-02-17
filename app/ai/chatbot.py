import os
import requests
from emotion_predictor import EmotionModel


class Chatbot:
    def __init__(self, model_dir: str, api_key: str = None):
        """
        初始化聊天机器人
        :param model_dir: TinyBERT 训练模型路径 (内含 mapping.txt)
        :param api_key: DeepSeek API Key (可选, 从环境变量 NEBULA_API_KEY 或直接传入)
        """
        # -- 用本地情感模型 --
        self.emotion_model = EmotionModel(model_dir)

        # -- 如果将来想用本地对话模型 (aimo.py) 而非API，可在此初始化 AIMO --
        # from aimo import AIMO
        # self.aimo = AIMO()

        self.api_key = api_key or os.environ.get("NEBULA_API_KEY")
        if not self.api_key:
            raise ValueError(" 未找到 API Key，请设置环境变量 NEBULA_API_KEY")

        # DeepSeek API 相关配置
        self.url = "https://inference.nebulablock.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 这里的 system_prompt 用于 API 的 "system" role 提示
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

    def query_deepseek(self, system_prompt: str, user_input: str):
        """
        发送消息到 DeepSeek API, 返回完整 JSON，方便后续解析
        :param system_prompt: system 角色的提示
        :param user_input: user 角色的内容
        :return: DeepSeek API 返回的 JSON
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        data = {
            "messages": messages,
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "max_tokens": 500,
            "temperature": 1.32,
            "top_p": 0.9,
            "stream": False
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()

    def chat(self, user_input: str):
        """
        运行聊天交互模式 (使用外部API进行对话)

        :param user_input: 用户输入的内容
        :return: DeepSeek API 生成的文本回复
        """
        initial_message = "你好啊人类，我是 AIMO#0001 号，很高兴见到你！今天感觉怎么样？"
        print(f"AIMO: {initial_message}")

        # 1. 分析情感
        emotions = self.emotion_model.predict(user_input)
        formatted_input = f"User input: {user_input} | Emotion: {', '.join(emotions) if emotions else 'neutral'}"
        print(f"🧠 识别情绪: {emotions}")

        # 2. 通过外部API生成回复
        deepseek_response = self.query_deepseek(self.system_prompt, formatted_input)
        # deepseek_response 是一个包含 "choices" ... 的JSON
        response_text = deepseek_response.get("choices", [{}])[0] \
                                        .get("message", {}) \
                                        .get("content", "❌ API 返回错误")

        return response_text
