# emotion_predictor.py
import os
import torch
from typing import List
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class EmotionModel:
    """
    EmotionModel 类用于加载 TinyBERT 情感分析模型，并进行情感预测。

    Attributes:
        device (str): 运行设备 ('cuda' 或 'cpu')。
        tokenizer (AutoTokenizer): 负责文本编码的分词器。
        model (AutoModelForSequenceClassification): 预训练的情感分类模型。
        emotion_labels (List[str]): 存储情感标签的列表。
    """

    def __init__(self, model_dir: str, device: str = None):
        """
        初始化情感分析模型

        :param model_dir: TinyBERT 预训练模型路径 (其中应包含 mapping.txt)
        :param device: 运行设备 ('cuda' 或 'cpu')，默认自动检测
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # 假设 mapping.txt 存在于同一模型目录下
        mapping_file = os.path.join(model_dir, "mapping.txt")
        if not os.path.exists(mapping_file):
            raise FileNotFoundError(f"情感标签映射文件不存在: {mapping_file}")

        # 加载情感标签
        with open(mapping_file, "r", encoding="utf-8") as f:
            self.emotion_labels = [line.strip() for line in f.readlines()]

        print(f"成功读取 {len(self.emotion_labels)} 个情感标签: {self.emotion_labels}")

        # 加载分词器 & 模型
        print(f"正在加载情感分析模型: {model_dir} 到 {self.device} ...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(self.device)
        self.model.eval()
        print(f"情感分析模型加载完成，运行设备: {self.device}")

    def predict(self, user_input: str, threshold: float = 0.5) -> List[str]:
        """
        预测输入文本的情感标签

        :param user_input: 用户输入的文本
        :param threshold: 预测的概率阈值 (默认 0.5)
        :return: 预测的情感标签列表
        """
        if not isinstance(user_input, str):
            raise ValueError("输入文本必须是字符串类型")

        # 对输入进行编码
        inputs = self.tokenizer(
            user_input,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        ).to(self.device)

        # 推理
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.sigmoid(outputs.logits).cpu().numpy().squeeze()

        # 选取大于阈值的情感标签
        predicted_labels = [
            self.emotion_labels[i]
            for i, p in enumerate(probabilities)
            if p > threshold
        ]

        return predicted_labels
