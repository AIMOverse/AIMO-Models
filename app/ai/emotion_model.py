import logging
import os
from pathlib import Path
from typing import List

import numpy
import torch
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

        # Get the absolute path of the current file directory
        current_dir = Path(__file__).parent

        # Use the correct mapping file path
        mapping_file = current_dir / "static" / "data" / "mapping.txt"

        # Get the absolute path of the model
        model_path = current_dir / "static" / "models" / "EmotionModule"

        if not mapping_file.exists():
            raise FileNotFoundError(f"Sentiment label mapping file does not exist: {mapping_file}")

        # Ensure the model directory exists
        if not model_path.exists():
            # If the model doesn't exist, try to download it from Hugging Face
            logging.info(f"Model directory does not exist: {model_path}. Attempting to download from Hugging Face...")
            try:
                os.environ["TRANSFORMERS_OFFLINE"] = "0"  # Allow online downloads
                os.makedirs(model_path, exist_ok=True)
                
                # Get Hugging Face token from environment variables
                hf_token = os.environ.get("HF_TOKEN")
                
                if hf_token:
                    logging.info("Using Hugging Face token from environment variable")
                    self.tokenizer = AutoTokenizer.from_pretrained("Wes1eyyy/AIMO-EmotionModule", use_auth_token=hf_token)
                    self.model = AutoModelForSequenceClassification.from_pretrained("Wes1eyyy/AIMO-EmotionModule", use_auth_token=hf_token)
                else:
                    logging.warning("No Hugging Face token provided, attempting anonymous access (may fail for private models)")
                    self.tokenizer = AutoTokenizer.from_pretrained("Wes1eyyy/AIMO-EmotionModule")
                    self.model = AutoModelForSequenceClassification.from_pretrained("Wes1eyyy/AIMO-EmotionModule")
                
                # Save the model locally
                self.tokenizer.save_pretrained(str(model_path))
                self.model.save_pretrained(str(model_path))
                logging.info(f"Model successfully downloaded and saved to {model_path}")
            except Exception as e:
                raise RuntimeError(f"Failed to download model from Hugging Face: {str(e)}")
        else:
            logging.info(f"Using locally cached model from: {model_path}")
            
        # Load emotion labels
        with open(mapping_file, "r", encoding="utf-8") as f:
            self.emotion_labels = [line.strip() for line in f.readlines()]

        # Load tokenizer and model
        logging.info(f"Loading sentiment analysis model: {model_path} to {self.device} ...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_path)).to(self.device)
        logging.info(f"Sentiment analysis model loaded, running on device: {self.device}")

    def predict(self, user_input: str, threshold: float = 0.5) -> List[str]:
        """
        Predict sentiment labels for the input text

        :param user_input: The input text from the user
        :param threshold: The probability threshold for prediction (default 0.5)
        :return: A list of predicted sentiment labels
        """
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
            self.emotion_labels[i] for i, p in enumerate(probabilities) if p > numpy.float32(threshold)
        ]

        return predicted_labels