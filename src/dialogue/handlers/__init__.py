"""
Intent Handlers - Factory Pattern.
Each handler processes a specific intent and returns a response.
"""

from src.dialogue.handlers.base import IntentHandler
from src.dialogue.handlers.factory import IntentHandlerFactory
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

__all__ = [
    "IntentHandler",
    "IntentHandlerFactory",
    "BalanceHandler",
    "TransactionHandler",
    "CardHandler",
    "LoanHandler",
    "ComplaintHandler",
    "GreetingHandler",
    "GoodbyeHandler",
    "FallbackHandler",
]