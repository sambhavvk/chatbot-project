"""
IntentHandlerFactory - Factory Pattern.
Creates the appropriate IntentHandler based on the classified intent.
"""

from typing import Dict, Type
from src.dialogue.handlers.base import IntentHandler
from src.dialogue.handlers.registry import (
    BalanceHandler,
    TransactionHandler,
    CardHandler,
    LoanHandler,
    ComplaintHandler,
    GreetingHandler,
    GoodbyeHandler,
    FallbackHandler,
)


class IntentHandlerFactory:
    """
    Factory that maps intent names to handler classes.
    Registered handlers are instantiated lazily on first use.
    """

    # Default mapping of intent name -> handler class
    _registry: Dict[str, Type[IntentHandler]] = {
        "balance": BalanceHandler,
        "transaction": TransactionHandler,
        "card": CardHandler,
        "loan": LoanHandler,
        "complaint": ComplaintHandler,
        "greeting": GreetingHandler,
        "goodbye": GoodbyeHandler,
    }

    def __init__(self) -> None:
        self._instances: Dict[str, IntentHandler] = {}

    def register(self, intent_name: str, handler_class: Type[IntentHandler]) -> None:
        """
        Register a new handler class for an intent.

        Args:
            intent_name: The intent name to handle.
            handler_class: The handler class (must be a subclass of IntentHandler).
        """
        self._registry[intent_name] = handler_class

    def get_handler(self, intent_name: str) -> IntentHandler:
        """
        Get or create a handler instance for the given intent.
        Falls back to FallbackHandler if the intent is not registered.

        Args:
            intent_name: The classified intent name.

        Returns:
            An IntentHandler instance ready to process the message.
        """
        if intent_name in self._instances:
            return self._instances[intent_name]

        handler_class = self._registry.get(intent_name)
        if handler_class is None:
            handler_class = FallbackHandler

        instance = handler_class()
        self._instances[intent_name] = instance
        return instance

    @property
    def registered_intents(self) -> list:
        """Return all registered intent names."""
        return list(self._registry.keys())