"""
DialogueManager - Core orchestration class.
Ties together intent classification, entity extraction, sentiment analysis,
intent handling, and escalation observation.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging
import uuid

from src.nlp.intent_classifier import IntentClassifier
from src.nlp.entity_extractor import EntityExtractor
from src.nlp.sentiment_analyzer import SentimentAnalyzer
from src.dialogue.handlers.factory import IntentHandlerFactory
from src.dialogue.escalator import SentimentEscalator

logger = logging.getLogger(__name__)


class DialogueManager:
    """
    Central dialogue engine that processes user messages and returns responses.
    Orchestrates the full NLP pipeline and delegates to intent handlers.
    """

    def __init__(
        self,
        intent_classifier: IntentClassifier,
        entity_extractor: EntityExtractor,
        sentiment_analyzer: SentimentAnalyzer,
        handler_factory: Optional[IntentHandlerFactory] = None,
        escalator: Optional[SentimentEscalator] = None,
    ) -> None:
        """
        Args:
            intent_classifier: Strategy for classifying user intent.
            entity_extractor: Component for NER extraction.
            sentiment_analyzer: Component for sentiment scoring.
            handler_factory: Factory to create intent handlers.
            escalator: Observer manager for sentiment escalation.
        """
        self._intent_classifier = intent_classifier
        self._entity_extractor = entity_extractor
        self._sentiment_analyzer = sentiment_analyzer
        self._handler_factory = handler_factory or IntentHandlerFactory()
        self._escalator = escalator or SentimentEscalator()

    def handle_message(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message through the full pipeline.

        Args:
            user_id: Unique identifier for the user.
            message: The raw text input from the user.
            context: Optional additional context (user profile, history, etc.).

        Returns:
            Dictionary containing:
                - response: The bot's text response.
                - intent: Classified intent name.
                - confidence: Intent confidence score.
                - entities: Extracted entities list.
                - sentiment: Sentiment analysis result.
                - escalated: Boolean indicating if escalation was triggered.
                - timestamp: ISO format timestamp.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        context = context or {}

        # Step 1: Classify intent
        intent_result = self._intent_classifier.classify(message)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]

        # Step 2: Extract entities
        entities = self._entity_extractor.extract(message)

        # Step 3: Analyze sentiment
        sentiment = self._sentiment_analyzer.analyze(message)

        # Step 4: Get the handler and generate response
        handler = self._handler_factory.get_handler(intent)
        response = handler.handle(message, entities, context)

        # Step 5: Check for sentiment escalation
        escalated = self._sentiment_analyzer.needs_escalation(message)
        if escalated:
            escalation_event = {
                "user_id": user_id,
                "message": message,
                "sentiment": sentiment,
                "intent": intent,
                "timestamp": timestamp,
                "escalation_id": str(uuid.uuid4()),
            }
            self._escalator.notify_escalation(escalation_event)

        result = {
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "sentiment": sentiment,
            "escalated": escalated,
            "timestamp": timestamp,
        }

        logger.info(
            "Processed message | user=%s | intent=%s | confidence=%.4f | escalated=%s",
            user_id,
            intent,
            confidence,
            escalated,
        )

        return result

    @property
    def handler_factory(self) -> IntentHandlerFactory:
        return self._handler_factory

    @property
    def escalator(self) -> SentimentEscalator:
        return self._escalator