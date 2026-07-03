"""
DynamoDB Client - DAO Pattern.
Abstracts all DynamoDB operations for conversations, escalations, and user profiles.
Supports both localstack (development) and real AWS DynamoDB.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)

# Table names
TABLE_CONVERSATIONS = "Conversations"
TABLE_ESCALATIONS = "EscalationRequests"
TABLE_USER_PROFILES = "UserProfiles"


class DynamoDBClient:
    """
    Data Access Object for DynamoDB operations.
    Handles conversation logging, escalation requests, and user profiles.

    Supports localstack by setting the ENDPOINT_URL environment variable
    or by passing endpoint_url directly.
    """

    def __init__(self, endpoint_url: Optional[str] = None, region_name: str = "eu-west-2") -> None:
        """
        Args:
            endpoint_url: Custom DynamoDB endpoint (e.g., http://localhost:4566 for localstack).
            region_name: AWS region name.
        """
        self._endpoint_url = endpoint_url or os.environ.get("DYNAMODB_ENDPOINT")
        self._region_name = region_name

        if self._endpoint_url:
            self._dynamodb = boto3.resource(
                "dynamodb",
                endpoint_url=self._endpoint_url,
                region_name=region_name,
                aws_access_key_id="fake",
                aws_secret_access_key="fake",
            )
        else:
            self._dynamodb = boto3.resource("dynamodb", region_name=region_name)

        self._ensure_tables()

    # ------------------------------------------------------------------
    # Table initialisation
    # ------------------------------------------------------------------

    def _ensure_tables(self) -> None:
        """Create tables if they don't exist (idempotent)."""
        existing = {t.name for t in self._dynamodb.tables.all()}
        if TABLE_CONVERSATIONS not in existing:
            self._create_conversations_table()
        if TABLE_ESCALATIONS not in existing:
            self._create_escalations_table()
        if TABLE_USER_PROFILES not in existing:
            self._create_user_profiles_table()

    def _create_conversations_table(self) -> None:
        self._dynamodb.create_table(
            TableName=TABLE_CONVERSATIONS,
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        logger.info("Created table: %s", TABLE_CONVERSATIONS)

    def _create_escalations_table(self) -> None:
        self._dynamodb.create_table(
            TableName=TABLE_ESCALATIONS,
            KeySchema=[
                {"AttributeName": "escalation_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "escalation_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        logger.info("Created table: %s", TABLE_ESCALATIONS)

    def _create_user_profiles_table(self) -> None:
        self._dynamodb.create_table(
            TableName=TABLE_USER_PROFILES,
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        logger.info("Created table: %s", TABLE_USER_PROFILES)

    # ------------------------------------------------------------------
    # Conversation operations
    # ------------------------------------------------------------------

    def save_message(
        self,
        user_id: str,
        message: str,
        response: str,
        intent: str,
        confidence: float,
        sentiment: Dict[str, float],
        escalated: bool = False,
    ) -> None:
        """
        Persist a conversation turn to DynamoDB.

        Args:
            user_id: Unique user identifier.
            message: User's input message.
            response: Bot's response.
            intent: Classified intent.
            confidence: Intent confidence score.
            sentiment: Sentiment analysis result dict.
            escalated: Whether escalation was triggered.
        """
        table = self._dynamodb.Table(TABLE_CONVERSATIONS)
        timestamp = datetime.now(timezone.utc).isoformat()

        item = {
            "user_id": user_id,
            "timestamp": timestamp,
            "message": message,
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "sentiment_compound": sentiment.get("compound", 0.0),
            "sentiment_pos": sentiment.get("pos", 0.0),
            "sentiment_neu": sentiment.get("neu", 0.0),
            "sentiment_neg": sentiment.get("neg", 0.0),
            "escalated": escalated,
        }
        table.put_item(Item=item)
        logger.debug("Saved message for user=%s, intent=%s", user_id, intent)

    def get_recent_conversation(
        self, user_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent conversation history for a user.

        Args:
            user_id: Unique user identifier.
            limit: Maximum number of messages to return.

        Returns:
            List of conversation items sorted by timestamp descending.
        """
        table = self._dynamodb.Table(TABLE_CONVERSATIONS)
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,  # descending by timestamp
            Limit=limit,
        )
        return response.get("Items", [])

    # ------------------------------------------------------------------
    # Escalation operations
    # ------------------------------------------------------------------

    def create_escalation_request(
        self,
        user_id: str,
        reason: str,
        sentiment: Optional[Dict[str, float]] = None,
        message: Optional[str] = None,
    ) -> str:
        """
        Create an escalation request record.

        Args:
            user_id: The user needing escalation.
            reason: Human-readable reason for escalation.
            sentiment: Optional sentiment scores at time of escalation.
            message: The message that triggered escalation.

        Returns:
            The generated escalation_id.
        """
        table = self._dynamodb.Table(TABLE_ESCALATIONS)
        escalation_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        item = {
            "escalation_id": escalation_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "reason": reason,
            "status": "pending",
        }
        if sentiment:
            item["sentiment"] = sentiment
        if message:
            item["message"] = message

        table.put_item(Item=item)
        logger.info("Created escalation request %s for user %s", escalation_id, user_id)
        return escalation_id

    def get_escalation(self, escalation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an escalation request by ID.

        Args:
            escalation_id: The escalation request ID.

        Returns:
            Escalation item dict, or None if not found.
        """
        table = self._dynamodb.Table(TABLE_ESCALATIONS)
        response = table.get_item(Key={"escalation_id": escalation_id})
        return response.get("Item")

    # ------------------------------------------------------------------
    # User profile operations
    # ------------------------------------------------------------------

    def save_user_profile(self, user_id: str, profile: Dict[str, Any]) -> None:
        """
        Create or update a user profile.

        Args:
            user_id: Unique user identifier.
            profile: Dictionary of profile attributes.
        """
        table = self._dynamodb.Table(TABLE_USER_PROFILES)
        item = {"user_id": user_id, **profile}
        table.put_item(Item=item)
        logger.debug("Saved profile for user=%s", user_id)

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user profile.

        Args:
            user_id: Unique user identifier.

        Returns:
            Profile dict, or None if not found.
        """
        table = self._dynamodb.Table(TABLE_USER_PROFILES)
        response = table.get_item(Key={"user_id": user_id})
        return response.get("Item")

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def list_tables(self) -> List[str]:
        """Return table names present in DynamoDB."""
        return [t.name for t in self._dynamodb.tables.all()]

    def table_exists(self, table_name: str) -> bool:
        """Check if a table already exists."""
        return table_name in self.list_tables()