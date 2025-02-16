import os
import requests
from app.ai.emotion_predictor import EmotionPredictor


class Chatbot:
    def __init__(self, model_dir: str, mapping_file: str, api_key: str = None):
        """
        初始化聊天机器人
        :param model_dir: TinyBERT 训练模型路径
        :param mapping_file: 情感标签映射文件
        :param api_key: DeepSeek API Key (可选)
        """
        self.emotion_predictor = EmotionPredictor(model_dir, mapping_file)
        self.api_key = api_key or os.environ.get("NEBULA_API_KEY")
        
        if not self.api_key:
            raise ValueError(" 未找到 API Key，请设置环境变量 NEBULA_API_KEY")

        self.url = "https://inference.nebulablock.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

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
                                                    New Lifeform  ;; As an AI lifeform, you have a unique perspective on the world, different from humans.)))) """

    def query_deepseek(self, user_input: str) -> str:
        """
        发送消息到 DeepSeek API
        :param user_input: 处理后的用户输入 (包含情感)
        :return: DeepSeek 生成的回复
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]

        data = {
            "messages": messages,
            "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
            "max_tokens": 300,
            "temperature": 1.32,
            "top_p": 0.9,
            "stream": False
        }

        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", " API 返回错误")

    def chat(self, user_input: str):
        """
        运行聊天交互模式
        """
        initial_message = "你好啊人类，我是 AIMO#0001 号，很高兴见到你！今天感觉怎么样？"
        print(f" AIMO: {initial_message}")
        
        # Step 1: 进行情感分析
        emotions = self.emotion_predictor.predict(user_input)
        formatted_input = f"User input: {user_input} | Emotion: {', '.join(emotions) if emotions else 'neutral'}"
        print(f"🧠 识别情绪: {emotions}")

        # Step 2: 发送到 DeepSeek API
        deepseek_response = self.query_deepseek(self.system_prompt, formatted_input)
        response_text = deepseek_response.get("choices", [{}])[0].get("message", {}).get("content", "❌ API 返回错误")

        return response_text
        
