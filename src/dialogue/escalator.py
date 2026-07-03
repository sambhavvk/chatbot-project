"""
Sentiment Escalator - Observer Pattern.
Listens for negative sentiment events and triggers escalation actions
(e.g., logging, notifying a human agent, writing to DynamoDB).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class SentimentObserver(ABC):
    """
    Observer interface for sentiment escalation events.
    Concrete implementations define what happens when escalation is triggered.
    """

    @abstractmethod
    def on_escalation(self, event: Dict[str, Any]) -> None:
        """
        Called when sentiment drops below the escalation threshold.

        Args:
            event: Dictionary containing escalation details:
                - user_id: The user who triggered the escalation.
                - message: The message that triggered it.
                - sentiment: The sentiment analysis result dict.
                - timestamp: ISO format timestamp.
        """
        pass


class LoggingEscalator(SentimentObserver):
    """Logs escalation events to the Python logger."""

    def on_escalation(self, event: Dict[str, Any]) -> None:
        logger.warning(
            "ESCALATION TRIGGERED | user=%s | compound=%.4f | message=%s",
            event.get("user_id", "unknown"),
            event.get("sentiment", {}).get("compound", 0.0),
            event.get("message", ""),
        )


class PrintEscalator(SentimentObserver):
    """Prints escalation events to stdout (for CLI demos)."""

    def on_escalation(self, event: Dict[str, Any]) -> None:
        print(
            "\n[ESCALATION ALERT] "
            f"User {event.get('user_id', 'unknown')} "
            "may need human intervention. "
            f"Sentiment: {event.get('sentiment', {})}"
        )


class CompositeEscalator(SentimentObserver):
    """
    Combines multiple observers so multiple escalation actions
    can happen simultaneously (e.g., log + print + DB write).
    """

    def __init__(self) -> None:
        self._observers: list[SentimentObserver] = []

    def add_observer(self, observer: SentimentObserver) -> None:
        """Register an additional observer."""
        self._observers.append(observer)

    def remove_observer(self, observer: SentimentObserver) -> None:
        """Remove a previously registered observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def on_escalation(self, event: Dict[str, Any]) -> None:
        for observer in self._observers:
            try:
                observer.on_escalation(event)
            except Exception as e:
                logger.error("Error in escalation observer %s: %s", observer, e)


class SentimentEscalator:
    """
    Manages sentiment observers and triggers them when escalation
    conditions are met. This is the Subject in the Observer pattern.
    """

    def __init__(self, observer: Optional[SentimentObserver] = None) -> None:
        self._observer: SentimentObserver = observer or CompositeEscalator()

    @property
    def observer(self) -> SentimentObserver:
        return self._observer

    def notify_escalation(self, event: Dict[str, Any]) -> None:
        """
        Notify all registered observers of an escalation event.

        Args:
            event: Escalation event data dict.
        """
        self._observer.on_escalation(event)