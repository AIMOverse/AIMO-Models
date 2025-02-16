import os
import torch
from typing import List
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class EmotionPredictor:
    def __init__(self, model_dir: str, mapping_file: str, device: str = None):
        """
        初始化情感分析模型
        :param model_dir: 训练好的 TinyBERT 模型路径
        :param mapping_file: 存储情感标签的文件
        :param device: 运行设备 (cpu/gpu)，默认自动检测
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # 加载情感标签
        if not os.path.exists(mapping_file):
            raise FileNotFoundError(f"情感标签映射文件不存在: {mapping_file}")
        
        with open(mapping_file, "r", encoding="utf-8") as f:
            self.emotion_labels = [line.strip() for line in f.readlines()]
        
        print(f"读取 {len(self.emotion_labels)} 个情感标签: {self.emotion_labels}")

        # 加载 Tokenizer & Model
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(self.device)
        self.model.eval()
        print(f" 模型加载完成，运行设备: {self.device}")

    def predict(self, text: str, threshold: float = 0.5) -> List[str]:
        """
        预测输入文本的情感标签
        :param text: 输入的文本
        :param threshold: 情感分类的概率阈值，默认 0.5
        :return: 预测的情感列表
        """
        if not isinstance(text, str):
            raise ValueError("输入文本必须是字符串类型")

        print(f"\n 输入文本: {text}")
        
        # Tokenization
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128).to(self.device)
        print(f" Tokenized Input: {inputs}")

        # 预测
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.sigmoid(outputs.logits).cpu().numpy().squeeze()
        
        print(f" Probabilities: {probabilities}")

        # 选择大于阈值的标签
        predicted_labels = [self.emotion_labels[i] for i, p in enumerate(probabilities) if p > threshold]
        print(f" 预测情绪: {predicted_labels}\n")

        return predicted_labels
