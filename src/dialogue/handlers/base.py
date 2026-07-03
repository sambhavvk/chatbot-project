"""
Abstract base class for intent handlers.
Each concrete handler implements handle() to process a specific intent.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class IntentHandler(ABC):
    """
    Abstract handler for a specific user intent.
    Subclasses implement the handle() method to generate responses.
    """

    @abstractmethod
    def handle(
        self, user_message: str, entities: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> str:
        """
        Process the user's message and return a bot response.

        Args:
            user_message: The original user input text.
            entities: List of extracted entities from the message.
            context: Additional context (user profile, conversation history, etc.).

        Returns:
            A string response from the bot.
        """
        pass

    @property
    @abstractmethod
    def intent_name(self) -> str:
        """The intent this handler is responsible for."""
        pass