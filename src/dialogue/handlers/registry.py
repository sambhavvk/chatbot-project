"""
Concrete intent handler implementations.
Each class handles a specific intent by generating appropriate responses.
"""

from typing import Dict, Any, List
from src.dialogue.handlers.base import IntentHandler


class BalanceHandler(IntentHandler):
    """Handles balance inquiry intents."""

    @property
    def intent_name(self) -> str:
        return "balance"

    def handle(
        self,
        user_message: str,
        entities: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        # In production, this would query a real account service
        account_name = context.get("account_name", "your account")
        balance = context.get("balance", "£1,250.75")
        return (
            f"The current balance for {account_name} is {balance}. "
            "Is there anything else I can help you with?"
        )


class TransactionHandler(IntentHandler):
    """Handles transaction/transfer/payment intents."""

    @property
    def intent_name(self) -> str:
        return "transaction"

    def handle(
        self,
        user_message: str,
        entities: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        money_entities = [e["text"] for e in entities if e["label"] == "MONEY"]
        if money_entities:
            amount = money_entities[0]
            return (
                f"I can help you transfer {amount}. "
                "To proceed, I'll need the recipient's sort code and account number. "
                "Would you like to continue?"
            )
        return (
            "I'd be happy to help with a transaction. "
            "Could you tell me the amount and the recipient's details?"
        )


class CardHandler(IntentHandler):
    """Handles card-related intents (report lost/stolen, apply, etc.)."""

    @property
    def intent_name(self) -> str:
        return "card"

    def handle(
        self,
        user_message: str,
        entities: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        # Check if this is a lost/stolen card report
        msg_lower = user_message.lower()
        if any(kw in msg_lower for kw in ["lost", "stolen", "missing", "block"]):
            return (
                "I'm sorry to hear your card is missing. For your security, "
                "I can immediately block your card and arrange a replacement. "
                "Would you like me to proceed with this?"
            )
        return (
            "I can help with card-related services including reporting a lost card, "
            "ordering a replacement, or checking your card details. "
            "What would you like to do?"
        )


class LoanHandler(IntentHandler):
    """Handles loan/mortgage intents."""

    @property
    def intent_name(self) -> str:
        return "loan"

    def handle(
        self,
        user_message: str,
        entities: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        return (
            "I can provide information about our loan and mortgage products. "
            "Our current personal loan rates start from 5.9% APR. "
            "Would you like me to connect you with a loan specialist, "
            "or would you prefer to browse our options online?"
        )


class ComplaintHandler(IntentHandler):
    """Handles complaint intents."""

    @property
    def intent_name(self) -> str:
        return "complaint"

    def handle(
        self,
        user_message: str,
        entities: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        return (
            "I understand you're experiencing an issue, and I want to help resolve it. "
            "I've logged your complaint and escalated it to our support team. "
            "A representative will review your case and get back to you within 24 hours. "
            "Your reference number is #SR-{date}-{random}. "
            "Is there anything else I can assist you with in the meantime?"
        )


class GreetingHandler(IntentHandler):
    """Handles greeting intents."""

    @property
    def intent_name(self) -> str:
        return "greeting"

    def handle(
        self,
        user_message: str,
        entities: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        user_name = context.get("user_name", "there")
        return (
            f"Hello {user_name}! Welcome to our virtual assistant. "
            "I can help with balance inquiries, transactions, card services, "
            "loans, and more. How can I assist you today?"
        )


class GoodbyeHandler(IntentHandler):
    """Handles goodbye intents."""

    @property
    def intent_name(self) -> str:
        return "goodbye"

    def handle(
        self,
        user_message: str,
        entities: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        return (
            "Thank you for chatting with us today! "
            "If you need further assistance, don't hesitate to reach out. "
            "Have a great day!"
        )


class FallbackHandler(IntentHandler):
    """Handles unknown/unclassified intents."""

    @property
    def intent_name(self) -> str:
        return "fallback"

    def handle(
        self,
        user_message: str,
        entities: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        return (
            "I'm not quite sure I understood that. Could you rephrase your request? "
            "I can help with balance checks, transactions, card services, loans, "
            "and account-related questions."
        )