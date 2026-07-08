"""
Tests for intent classifier implementations.
"""

import pytest
from src.nlp.intent_classifier import MockIntentClassifier, IntentClassifier


class TestMockIntentClassifier:
    """Tests for MockIntentClassifier."""

    @pytest.fixture
    def classifier(self):
        return MockIntentClassifier()

    def test_is_intent_classifier(self, classifier):
        """Mock should be an instance of IntentClassifier (Strategy pattern)."""
        assert isinstance(classifier, IntentClassifier)

    def test_classify_balance_intent(self, classifier):
        result = classifier.classify("What is my account balance please?")
        assert result["intent"] == "balance"
        assert 0 <= result["confidence"] <= 1

    def test_classify_transaction_intent(self, classifier):
        result = classifier.classify("I want to send a payment to my friend")
        assert result["intent"] == "transaction"
        assert result["confidence"] > 0

    def test_classify_card_intent(self, classifier):
        result = classifier.classify("My credit card is lost")
        assert result["intent"] == "card"

    def test_classify_complaint_intent(self, classifier):
        result = classifier.classify("I have a serious complaint about your service")
        assert result["intent"] == "complaint"
        assert result["confidence"] > 0

    def test_classify_greeting(self, classifier):
        result = classifier.classify("Hello! Good morning!")
        assert result["intent"] == "greeting"

    def test_classify_goodbye(self, classifier):
        result = classifier.classify("Bye, see you later!")
        assert result["intent"] == "goodbye"

    def test_classify_unknown(self, classifier):
        result = classifier.classify("xyzzy foobar blarg")
        assert result["intent"] == "unknown"
        assert result["confidence"] == 0.0

    def test_confidence_capped_at_one(self, classifier):
        """Confidence should never exceed 1.0."""
        result = classifier.classify(
            "balance transfer card loan complaint hello goodbye"
        )
        assert result["confidence"] <= 1.0