"""
Sentiment Analyzer Module - Uses VADER for lightweight sentiment scoring.
Provides compound polarity scores and a convenience method to check
if sentiment requires escalation.
"""

from typing import Dict, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentAnalyzer:
    """
    Wraps VADER SentimentIntensityAnalyzer.
    Provides compound sentiment scores and escalation threshold checking.
    """

    # Threshold below which sentiment is considered "escalation-worthy"
    DEFAULT_ESCALATION_THRESHOLD: float = -0.3

    def __init__(self, escalation_threshold: float = DEFAULT_ESCALATION_THRESHOLD) -> None:
        """
        Args:
            escalation_threshold: Compound score below which escalation is triggered.
        """
        self._analyzer = SentimentIntensityAnalyzer()
        self._escalation_threshold = escalation_threshold

    @property
    def escalation_threshold(self) -> float:
        return self._escalation_threshold

    def analyze(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a text string.

        Args:
            text: The user's message.

        Returns:
            Dictionary with keys: 'neg', 'neu', 'pos', 'compound'.
        """
        scores = self._analyzer.polarity_scores(text)
        return {
            "neg": round(scores["neg"], 4),
            "neu": round(scores["neu"], 4),
            "pos": round(scores["pos"], 4),
            "compound": round(scores["compound"], 4),
        }

    def needs_escalation(self, text: str) -> bool:
        """
        Check if sentiment is negative enough to warrant escalation.

        Args:
            text: The user's message.

        Returns:
            True if compound score is below the escalation threshold.
        """
        scores = self.analyze(text)
        return scores["compound"] < self._escalation_threshold

    def get_compound(self, text: str) -> float:
        """
        Convenience method to get the compound sentiment score directly.

        Args:
            text: The user's message.

        Returns:
            Compound polarity score between -1 (negative) and +1 (positive).
        """
        return self.analyze(text)["compound"]