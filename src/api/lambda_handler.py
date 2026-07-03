"""
AWS Lambda Handler - Entry point for API Gateway integration.
Wraps the DialogueManager as a serverless function.
"""

import json
import logging
import os
from typing import Dict, Any

from src.nlp.intent_classifier import MockIntentClassifier, BertIntentClassifier
from src.nlp.entity_extractor import EntityExtractor
from src.nlp.sentiment_analyzer import SentimentAnalyzer
from src.dialogue.manager import DialogueManager
from src.dialogue.escalator import SentimentEscalator, LoggingEscalator
from src.storage.dynamodb_client import DynamoDBClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Lazy-loaded singleton components
_manager: DialogueManager = None
_db_client: DynamoDBClient = None


def _get_manager() -> DialogueManager:
    """Lazily initialise the DialogueManager singleton."""
    global _manager, _db_client

    if _manager is not None:
        return _manager

    model_path = os.environ.get("MODEL_PATH", "models/intent_model")

    # Choose classifier based on whether model exists
    if os.path.isdir(model_path):
        try:
            classifier = BertIntentClassifier(model_path)
            logger.info("Using BERT intent classifier from %s", model_path)
        except Exception as e:
            logger.warning("Failed to load BERT model: %s. Falling back to mock.", e)
            classifier = MockIntentClassifier()
    else:
        logger.info("Model path %s not found. Using mock classifier.", model_path)
        classifier = MockIntentClassifier()

    entity_extractor = EntityExtractor()
    sentiment_analyzer = SentimentAnalyzer()

    escalator = SentimentEscalator()
    escalator._observer = LoggingEscalator()

    _manager = DialogueManager(
        intent_classifier=classifier,
        entity_extractor=entity_extractor,
        sentiment_analyzer=sentiment_analyzer,
        escalator=escalator,
    )

    # Initialise DB client if DynamoDB endpoint is configured
    dynamodb_endpoint = os.environ.get("DYNAMODB_ENDPOINT")
    if dynamodb_endpoint:
        _db_client = DynamoDBClient(endpoint_url=dynamodb_endpoint)

    return _manager


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for API Gateway integration.

    Expected event format (API Gateway Lambda proxy):
    {
        "body": "{\"user_id\": \"user123\", \"message\": \"What's my balance?\"}",
        ...
    }

    Args:
        event: API Gateway proxy event.
        context: Lambda execution context.

    Returns:
        API Gateway proxy response dict.
    """
    try:
        # Parse request body
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event

        user_id = body.get("user_id", "anonymous")
        message = body.get("message", "")

        if not message:
            return _response(400, {"error": "message field is required"})

        manager = _get_manager()
        result = manager.handle_message(user_id, message)

        # Persist to DynamoDB if available
        global _db_client
        if _db_client:
            try:
                _db_client.save_message(
                    user_id=user_id,
                    message=message,
                    response=result["response"],
                    intent=result["intent"],
                    confidence=result["confidence"],
                    sentiment=result["sentiment"],
                    escalated=result["escalated"],
                )
                if result["escalated"]:
                    _db_client.create_escalation_request(
                        user_id=user_id,
                        reason=f"Negative sentiment detected: compound={result['sentiment']['compound']}",
                        sentiment=result["sentiment"],
                        message=message,
                    )
            except Exception as e:
                logger.error("Failed to persist to DynamoDB: %s", e)

        return _response(200, result)

    except Exception as e:
        logger.exception("Error processing request")
        return _response(500, {"error": str(e)})


def _response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Build an API Gateway-compatible response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body),
    }


def warmup_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda warmup handler to pre-initialise the model on cold start.
    Called by CloudWatch scheduled events.
    """
    _get_manager()
    return {"statusCode": 200, "body": "Warmed up"}