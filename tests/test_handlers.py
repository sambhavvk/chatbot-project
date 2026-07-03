"""
Tests for intent handlers and the factory pattern.
"""

import pytest
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
from src.dialogue.handlers.factory import IntentHandlerFactory


class TestHandlers:
    """Tests for each concrete handler."""

    def test_balance_handler(self):
        handler = BalanceHandler()
        assert handler.intent_name == "balance"
        response = handler.handle("What's my balance?", [], {"balance": "£500.00"})
        assert "£500.00" in response

    def test_transaction_handler(self):
        handler = TransactionHandler()
        assert handler.intent_name == "transaction"
        response = handler.handle("Send £50", [{"text": "£50", "label": "MONEY"}], {})
        assert "£50" in response

    def test_transaction_handler_no_amount(self):
        handler = TransactionHandler()
        response = handler.handle("I want to transfer", [], {})
        assert "amount" in response.lower()

    def test_card_handler_lost(self):
        handler = CardHandler()
        response = handler.handle("My card is lost", [], {})
        assert "block" in response.lower()

    def test_card_handler_general(self):
        handler = CardHandler()
        response = handler.handle("Tell me about cards", [], {})
        assert "card" in response.lower()

    def test_loan_handler(self):
        handler = LoanHandler()
        assert handler.intent_name == "loan"
        response = handler.handle("I want a loan", [], {})
        assert "loan" in response.lower()

    def test_complaint_handler(self):
        handler = ComplaintHandler()
        response = handler.handle("I have a problem!", [], {})
        assert "complaint" in response.lower()

    def test_greeting_handler(self):
        handler = GreetingHandler()
        response = handler.handle("Hello!", [], {"user_name": "Alice"})
        assert "Alice" in response

    def test_goodbye_handler(self):
        handler = GoodbyeHandler()
        response = handler.handle("Bye!", [], {})
        assert len(response) > 0

    def test_fallback_handler(self):
        handler = FallbackHandler()
        assert handler.intent_name == "fallback"
        response = handler.handle("???", [], {})
        assert "rephrase" in response.lower()

    def test_all_handlers_subclass(self):
        """All handlers should inherit from IntentHandler."""
        for cls in [
            BalanceHandler,
            TransactionHandler,
            CardHandler,
            LoanHandler,
            ComplaintHandler,
            GreetingHandler,
            GoodbyeHandler,
            FallbackHandler,
        ]:
            assert issubclass(cls, IntentHandler)


class TestIntentHandlerFactory:
    """Tests for the Factory pattern."""

    @pytest.fixture
    def factory(self):
        return IntentHandlerFactory()

    def test_get_balance_handler(self, factory):
        handler = factory.get_handler("balance")
        assert isinstance(handler, BalanceHandler)

    def test_get_transaction_handler(self, factory):
        handler = factory.get_handler("transaction")
        assert isinstance(handler, TransactionHandler)

    def test_get_unknown_handler_falls_back(self, factory):
        handler = factory.get_handler("nonexistent_intent")
        assert isinstance(handler, FallbackHandler)

    def test_handler_caching(self, factory):
        """Factory should cache handler instances (singleton per intent)."""
        h1 = factory.get_handler("balance")
        h2 = factory.get_handler("balance")
        assert h1 is h2

    def test_register_new_handler(self, factory):
        class CustomHandler(IntentHandler):
            @property
            def intent_name(self):
                return "custom"

            def handle(self, msg, ents, ctx):
                return "custom response"

        factory.register("custom", CustomHandler)
        handler = factory.get_handler("custom")
        assert isinstance(handler, CustomHandler)
        assert handler.intent_name == "custom"

    def test_registered_intents(self, factory):
        intents = factory.registered_intents
        assert "balance" in intents
        assert "transaction" in intents
        assert "complaint" in intents