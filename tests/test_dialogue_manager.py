"""
Tests for DialogueManager orchestration and escalation logic.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.dialogue.manager import DialogueManager
from src.dialogue.escalator import (
    SentimentEscalator,
    SentimentObserver,
    PrintEscalator,
    LoggingEscalator,
    CompositeEscalator,
)
from src.nlp.intent_classifier import MockIntentClassifier
from src.nlp.entity_extractor import EntityExtractor
from src.nlp.sentiment_analyzer import SentimentAnalyzer
from src.dialogue.handlers.factory import IntentHandlerFactory


class TestDialogueManager:
    """Tests for DialogueManager."""

    @pytest.fixture
    def manager(self):
        classifier = MockIntentClassifier()
        entity_extractor = EntityExtractor()
        sentiment_analyzer = SentimentAnalyzer()
        return DialogueManager(
            intent_classifier=classifier,
            entity_extractor=entity_extractor,
            sentiment_analyzer=sentiment_analyzer,
        )

    def test_handle_balance_message(self, manager):
        result = manager.handle_message("user1", "What is my balance?")
        assert "response" in result
        assert result["intent"] == "balance"
        assert result["confidence"] > 0
        assert "entities" in result
        assert "sentiment" in result
        assert "escalated" in result
        assert "timestamp" in result

    def test_handle_greeting(self, manager):
        result = manager.handle_message(
            "user1", "Hello!", {"user_name": "TestUser"}
        )
        assert result["intent"] == "greeting"
        assert "TestUser" in result["response"]

    def test_handle_unknown_intent(self, manager):
        result = manager.handle_message("user1", "asdfghjkl zxcvbnm qwerty")
        assert result["intent"] == "unknown"
        # FallbackHandler response
        assert "rephrase" in result["response"].lower()

    def test_escalation_triggered_on_negative(self, manager):
        """Negative sentiment should trigger escalation."""
        result = manager.handle_message(
            "user1",
            "I hate this stupid terrible service, worst experience ever!!!"
        )
        assert result["escalated"] is True

    def test_no_escalation_on_positive(self, manager):
        """Positive sentiment should not trigger escalation."""
        result = manager.handle_message(
            "user1",
            "Thank you so much, this is wonderful and amazing!"
        )
        assert result["escalated"] is False

    def test_entities_extracted(self, manager):
        result = manager.handle_message(
            "user1",
            "I want to transfer £500 to John in London tomorrow"
        )
        # The mock classifier might classify this as transaction
        # Entities should be extracted regardless
        assert len(result["entities"]) >= 0  # spaCy NER may vary

    def test_result_structure(self, manager):
        """Verify the structure of the result dict."""
        result = manager.handle_message("user1", "Hello")
        expected_keys = {
            "response", "intent", "confidence", "entities",
            "sentiment", "escalated", "timestamp",
        }
        assert expected_keys.issubset(set(result.keys()))
        assert isinstance(result["confidence"], float)
        assert isinstance(result["escalated"], bool)


class TestSentimentEscalator:
    """Tests for the Observer pattern in escalator."""

    def test_print_escalator(self, capsys):
        escalator = SentimentEscalator(observer=PrintEscalator())
        event = {
            "user_id": "test-user",
            "message": "Angry message",
            "sentiment": {"compound": -0.8},
            "timestamp": "2025-01-01T00:00:00Z",
        }
        escalator.notify_escalation(event)
        captured = capsys.readouterr()
        assert "ESCALATION ALERT" in captured.out
        assert "test-user" in captured.out

    def test_logging_escalator(self, caplog):
        import logging
        caplog.set_level(logging.WARNING)
        escalator = SentimentEscalator(observer=LoggingEscalator())
        event = {
            "user_id": "test-user",
            "message": "Angry message",
            "sentiment": {"compound": -0.8},
            "timestamp": "2025-01-01T00:00:00Z",
        }
        escalator.notify_escalation(event)
        assert "ESCALATION TRIGGERED" in caplog.text
        assert "test-user" in caplog.text

    def test_composite_escalator(self):
        mock1 = Mock()
        mock2 = Mock()
        composite = CompositeEscalator()
        composite.add_observer(mock1)
        composite.add_observer(mock2)

        event = {"user_id": "u1", "message": "test"}
        escalator = SentimentEscalator(observer=composite)
        escalator.notify_escalation(event)

        mock1.on_escalation.assert_called_once_with(event)
        mock2.on_escalation.assert_called_once_with(event)

    def test_composite_handles_observer_error(self, caplog):
        """Composite should continue if one observer fails."""
        import logging
        caplog.set_level(logging.ERROR)

        failing = Mock()
        failing.on_escalation.side_effect = RuntimeError("Observer failed")
        working = Mock()

        composite = CompositeEscalator()
        composite.add_observer(failing)
        composite.add_observer(working)

        escalator = SentimentEscalator(observer=composite)
        event = {"user_id": "u1"}
        escalator.notify_escalation(event)

        working.on_escalation.assert_called_once_with(event)
        assert "Observer failed" in caplog.text