"""
CLI Chatbot Loop - Interactive command-line interface for testing the chatbot.
Run with: python -m src.dialogue.cli
"""

import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.nlp.intent_classifier import MockIntentClassifier, BertIntentClassifier
from src.nlp.entity_extractor import EntityExtractor
from src.nlp.sentiment_analyzer import SentimentAnalyzer
from src.dialogue.manager import DialogueManager
from src.dialogue.escalator import (
    SentimentEscalator,
    PrintEscalator,
    LoggingEscalator,
    CompositeEscalator,
)
from src.storage.dynamodb_client import DynamoDBClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def print_banner() -> None:
    """Print welcome banner."""
    print("=" * 60)
    print("  🤖  CUSTOMER SUPPORT CHATBOT - CLI DEMO  🤖")
    print("=" * 60)
    print()
    print("Type your message and press Enter. Commands:")
    print("  /help     - Show this help")
    print("  /history  - Show recent conversation (if DB enabled)")
    print("  /quit     - Exit the chatbot")
    print("=" * 60)
    print()


def build_manager(use_mock: bool = True, use_db: bool = False) -> DialogueManager:
    """
    Build the DialogueManager with appropriate components.

    Args:
        use_mock: Use MockIntentClassifier (True) or BERT model (False).
        use_db: Connect to DynamoDB (localstack) for persistence.

    Returns:
        Configured DialogueManager instance.
    """
    # Intent classifier
    if use_mock:
        classifier = MockIntentClassifier()
        logger.info("Using MockIntentClassifier")
    else:
        model_path = os.environ.get("MODEL_PATH", "models/intent_model")
        try:
            classifier = BertIntentClassifier(model_path)
            logger.info("Using BertIntentClassifier from %s", model_path)
        except Exception as e:
            logger.warning("Failed to load BERT model: %s. Falling back to mock.", e)
            classifier = MockIntentClassifier()

    entity_extractor = EntityExtractor()
    sentiment_analyzer = SentimentAnalyzer()

    # Escalator with composite observer (print + log)
    composite = CompositeEscalator()
    composite.add_observer(PrintEscalator())
    composite.add_observer(LoggingEscalator())
    escalator = SentimentEscalator(observer=composite)

    manager = DialogueManager(
        intent_classifier=classifier,
        entity_extractor=entity_extractor,
        sentiment_analyzer=sentiment_analyzer,
        escalator=escalator,
    )

    return manager


def interactive_loop(manager: DialogueManager, db_client=None) -> None:
    """
    Run the interactive CLI chatbot loop.

    Args:
        manager: Configured DialogueManager.
        db_client: Optional DynamoDBClient for persistence.
    """
    print_banner()
    user_id = "cli-user-001"
    context = {
        "user_name": "Sam",
        "account_name": "Current Account",
        "balance": "£2,450.30",
    }

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.lower() in ("/quit", "/exit", "/q"):
            print("Bot: Goodbye! Have a great day!")
            break
        elif user_input.lower() in ("/help", "/h"):
            print_banner()
            continue
        elif user_input.lower() in ("/history",):
            if db_client:
                messages = db_client.get_recent_conversation(user_id, limit=5)
                if messages:
                    print("\n--- Recent conversation ---")
                    for msg in reversed(messages):
                        print(f"  [{msg['timestamp']}] You: {msg['message']}")
                        print(f"  Bot: {msg['response']}")
                    print("--- End ---\n")
                else:
                    print("No conversation history found.")
            else:
                print("Database not connected. Run with --db flag to enable persistence.")
            continue

        # Process message
        result = manager.handle_message(user_id, user_input, context)

        print(f"Bot: {result['response']}")
        print(f"     [intent: {result['intent']}, "
              f"confidence: {result['confidence']:.2f}, "
              f"sentiment: {result['sentiment']['compound']:.2f}]")

        if result["escalated"]:
            print("     ⚠️  ESCALATION TRIGGERED - Human agent notified")

        # Persist to DB if enabled
        if db_client:
            try:
                db_client.save_message(
                    user_id=user_id,
                    message=user_input,
                    response=result["response"],
                    intent=result["intent"],
                    confidence=result["confidence"],
                    sentiment=result["sentiment"],
                    escalated=result["escalated"],
                )
                if result["escalated"]:
                    db_client.create_escalation_request(
                        user_id=user_id,
                        reason="Sentiment escalation from CLI",
                        sentiment=result["sentiment"],
                        message=user_input,
                    )
            except Exception as e:
                logger.error("DB persistence error: %s", e)

        print()


def main() -> None:
    """Main entry point for CLI chatbot."""
    use_mock = "--bert" not in sys.argv
    use_db = "--db" in sys.argv

    db_client = None
    if use_db:
        dynamodb_endpoint = os.environ.get(
            "DYNAMODB_ENDPOINT", "http://localhost:4566"
        )
        try:
            db_client = DynamoDBClient(endpoint_url=dynamodb_endpoint)
            logger.info("Connected to DynamoDB at %s", dynamodb_endpoint)
        except Exception as e:
            logger.warning("Failed to connect to DynamoDB: %s", e)
            logger.warning("Continuing without persistence...")

    manager = build_manager(use_mock=use_mock, use_db=use_db)
    interactive_loop(manager, db_client)


if __name__ == "__main__":
    main()