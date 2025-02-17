import logging

import torch
from pathlib import Path
from typing import List
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class EmotionModel:
    """
    EmotionModel class for loading the TinyBERT sentiment analysis model and performing sentiment prediction.

    Attributes:
        device (str): The device to run on ('cuda' or 'cpu').
        tokenizer (AutoTokenizer): The tokenizer responsible for text encoding.
        model (AutoModelForSequenceClassification): The pre-trained sentiment classification model.
        emotion_labels (List[str]): A list of sentiment labels.
    """

    def __init__(self):
        """
        Initialize the sentiment analysis model

        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Get the absolute path of the current file's directory
        current_dir = Path(__file__).parent

        # Use the correct mapping file path
        mapping_file = current_dir / "static" / "data" / "mapping.txt"

        # Get the absolute path of the model
        model_path = current_dir / "static" / "models" / "EmotionModule"

        if not mapping_file.exists():
            raise FileNotFoundError(f"Sentiment label mapping file does not exist: {mapping_file}")

        # Ensure the model directory exists
        if not model_path.exists():
            raise FileNotFoundError(f"Model directory does not exist: {model_path}")

        # Load sentiment labels
        with open(mapping_file, "r", encoding="utf-8") as f:
            self.emotion_labels = [line.strip() for line in f.readlines()]

        # Load tokenizer & model using absolute path
        logging.info(f"Loading sentiment analysis model: {model_path} to {self.device} ...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_path)).to(self.device)
        self.model.eval()
        logging.info(f"Sentiment analysis model loaded, running on device: {self.device}")

    def predict(self, user_input: str, threshold: float = 0.5) -> List[str]:
        """
        Predict sentiment labels for the input text

        :param user_input: The input text from the user
        :param threshold: The probability threshold for prediction (default 0.5)
        :return: A list of predicted sentiment labels
        """
        if not isinstance(user_input, str):
            raise ValueError("Input text must be of string type")

        # Encode the input
        inputs = self.tokenizer(
            user_input,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        ).to(self.device)

        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.sigmoid(outputs.logits).cpu().numpy().squeeze()

        # Select sentiment labels above the threshold
        predicted_labels = [
            self.emotion_labels[i]
            for i, p in enumerate(probabilities)
            if p > threshold
        ]

        return predicted_labels