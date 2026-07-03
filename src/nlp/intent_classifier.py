"""
Intent Classifier Module - Strategy Pattern
Provides an abstract base class and concrete implementations
for intent classification using different models.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import torch
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    pipeline,
)


class IntentClassifier(ABC):
    """
    Abstract base class for intent classifiers (Strategy Pattern).
    Allows swapping different classification models without changing
    the DialogueManager code.
    """

    @abstractmethod
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify the intent of a user message.

        Args:
            text: The user's input message.

        Returns:
            Dictionary with keys: 'intent' (str), 'confidence' (float).
        """
        pass


class MockIntentClassifier(IntentClassifier):
    """
    Mock implementation for unit testing and development.
    Returns predefined intents without needing a trained model.
    """

    def __init__(self) -> None:
        self._intents = {
            "balance": ["balance", "money", "account", "how much"],
            "transaction": ["transfer", "send", "payment", "pay"],
            "card": ["card", "credit", "debit", "atm"],
            "loan": ["loan", "mortgage", "borrow"],
            "complaint": ["complaint", "issue", "problem", "unhappy", "wrong"],
            "greeting": ["hello", "hi", "hey", "good morning"],
            "goodbye": ["bye", "goodbye", "see you"],
        }

    def classify(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        best_intent = "unknown"
        best_score = 0.0

        for intent, keywords in self._intents.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_intent = intent

        confidence = min(best_score / 3.0, 1.0)
        return {"intent": best_intent, "confidence": round(confidence, 4)}


class BertIntentClassifier(IntentClassifier):
    """
    Intent classifier using a fine-tuned DistilBERT model.
    Uses GPU (CUDA) if available, falls back to CPU.
    """

    def __init__(self, model_path: str) -> None:
        """
        Args:
            model_path: Path to the saved fine-tuned model directory.
        """
        self._device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self._tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
        self._model = DistilBertForSequenceClassification.from_pretrained(
            model_path
        ).to(self._device)
        self._model.eval()

        # Build id-to-label mapping from model config
        self._id2label = self._model.config.id2label
        self._classifier = pipeline(
            "text-classification",
            model=self._model,
            tokenizer=self._tokenizer,
            device=0 if torch.cuda.is_available() else -1,
        )

    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def num_labels(self) -> int:
        return len(self._id2label)

    def classify(self, text: str) -> Dict[str, Any]:
        result = self._classifier(text)[0]
        # Map label to short intent name
        label = result["label"]
        # Handle both formats: "LABEL_0" style or plain intent names
        if label.startswith("LABEL_"):
            intent_id = int(label.split("_")[1])
            intent = self._id2label.get(intent_id, label)
        else:
            intent = label

        return {"intent": intent, "confidence": round(result["score"], 4)}