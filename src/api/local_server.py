"""
Local FastAPI Server - Wraps the DialogueManager as a REST API
for local development. The frontend can call this directly.

Run with: uvicorn src.api.local_server:app --host 0.0.0.0 --port 8080
"""

import logging
import os
import sys
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.nlp.intent_classifier import MockIntentClassifier, BertIntentClassifier
from src.nlp.entity_extractor import EntityExtractor
from src.nlp.sentiment_analyzer import SentimentAnalyzer
from src.dialogue.manager import DialogueManager
from src.dialogue.escalator import SentimentEscalator, PrintEscalator, LoggingEscalator, CompositeEscalator
from src.storage.dynamodb_client import DynamoDBClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Customer Support Chatbot API",
    description="AI-powered customer support chatbot with intent classification and sentiment analysis.",
    version="1.0.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lazy-loaded components
# ---------------------------------------------------------------------------

_manager: Optional[DialogueManager] = None
_db_client: Optional[DynamoDBClient] = None


def get_manager() -> DialogueManager:
    """Lazily initialise and return the DialogueManager singleton."""
    global _manager, _db_client

    if _manager is not None:
        return _manager

    model_path = os.environ.get("MODEL_PATH", "models/intent_model")

    # Choose classifier
    if os.path.isdir(model_path):
        try:
            classifier = BertIntentClassifier(model_path)
            logger.info("Using BERT intent classifier from %s", model_path)
        except Exception as e:
            logger.warning("Failed to load BERT model: %s. Falling back to mock.", e)
            classifier = MockIntentClassifier()
    else:
        logger.info("Model not found at %s. Using mock classifier.", model_path)
        classifier = MockIntentClassifier()

    entity_extractor = EntityExtractor()
    sentiment_analyzer = SentimentAnalyzer()

    # Composite escalator: log + print
    composite = CompositeEscalator()
    composite.add_observer(PrintEscalator())
    composite.add_observer(LoggingEscalator())
    escalator = SentimentEscalator(observer=composite)

    _manager = DialogueManager(
        intent_classifier=classifier,
        entity_extractor=entity_extractor,
        sentiment_analyzer=sentiment_analyzer,
        escalator=escalator,
    )

    # Initialise DB if localstack is available
    dynamodb_endpoint = os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:4566")
    try:
        _db_client = DynamoDBClient(endpoint_url=dynamodb_endpoint)
        logger.info("Connected to DynamoDB at %s", dynamodb_endpoint)
    except Exception as e:
        logger.warning("DynamoDB not available: %s. Running without persistence.", e)
        _db_client = None

    return _manager


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    user_id: str = "anonymous"
    message: str


class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    entities: list = []
    sentiment: dict = {}
    escalated: bool = False
    timestamp: str = ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "service": "Customer Support Chatbot API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Process a user message and return the chatbot response.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message field is required")

    try:
        manager = get_manager()
        result = manager.handle_message(
            user_id=request.user_id,
            message=request.message,
        )

        # Persist to DynamoDB if available
        global _db_client
        if _db_client:
            try:
                _db_client.save_message(
                    user_id=request.user_id,
                    message=request.message,
                    response=result["response"],
                    intent=result["intent"],
                    confidence=result["confidence"],
                    sentiment=result["sentiment"],
                    escalated=result["escalated"],
                )
                if result["escalated"]:
                    _db_client.create_escalation_request(
                        user_id=request.user_id,
                        reason=(
                            "Negative sentiment: "
                            f"compound={result['sentiment']['compound']}"
                        ),
                        sentiment=result["sentiment"],
                        message=request.message,
                    )
            except Exception as e:
                logger.error("Failed to persist to DynamoDB: %s", e)

        return ChatResponse(**result)

    except Exception as e:
        logger.exception("Error processing chat request")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Startup event
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup_event():
    """Warm up the model on server start."""
    logger.info("Starting up chatbot API server...")
    get_manager()
    logger.info("Chatbot API server ready.")