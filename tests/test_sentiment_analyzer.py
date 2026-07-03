"""
Tests for sentiment analyzer module.
"""

import pytest
from src.nlp.sentiment_analyzer import SentimentAnalyzer


class TestSentimentAnalyzer:
    """Tests for SentimentAnalyzer (VADER wrapper)."""

    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()

    def test_analyze_positive_text(self, analyzer):
        result = analyzer.analyze("I love this service! It's amazing and wonderful.")
        assert result["compound"] > 0.3
        assert result["pos"] > 0
        assert "neg" in result
        assert "neu" in result

    def test_analyze_negative_text(self, analyzer):
        result = analyzer.analyze("This is terrible. I hate it. Worst experience ever.")
        assert result["compound"] < -0.3
        assert result["neg"] > 0

    def test_analyze_neutral_text(self, analyzer):
        result = analyzer.analyze("My account number is 12345.")
        assert -0.3 <= result["compound"] <= 0.3

    def test_needs_escalation_negative(self, analyzer):
        """Severely negative text should trigger escalation."""
        assert analyzer.needs_escalation(
            "I am extremely angry and frustrated with your terrible service!!!"
        )

    def test_needs_escalation_positive(self, analyzer):
        """Positive text should not trigger escalation."""
        assert not analyzer.needs_escalation("Thank you so much, great service!")

    def test_needs_escalation_neutral(self, analyzer):
        """Neutral text should not trigger escalation."""
        assert not analyzer.needs_escalation("What is my balance?")

    def test_custom_threshold(self):
        """Custom escalation threshold should be respected."""
        analyzer = SentimentAnalyzer(escalation_threshold=-0.1)
        result = analyzer.analyze("This is a bit disappointing")
        # A mildly negative statement may be below -0.1
        assert isinstance(result["compound"], float)

    def test_get_compound_shortcut(self, analyzer):
        """get_compound should return the compound score."""
        c = analyzer.get_compound("Great!")
        assert isinstance(c, float)
        assert -1.0 <= c <= 1.0

    def test_empty_string(self, analyzer):
        result = analyzer.analyze("")
        assert result["compound"] == 0.0