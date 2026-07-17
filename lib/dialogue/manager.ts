/**
 * Dialogue Manager - TypeScript Port
 * Central orchestration class that ties together intent classification,
 * entity extraction, sentiment analysis, intent handling, and escalation.
 * Replaces the Python DialogueManager.
 */

import { v4 as uuidv4 } from "uuid";
import {
  classifyIntent,
  extractEntities,
  analyzeSentiment,
  needsEscalation,
  type Entity,
  type SentimentResult,
} from "@/lib/nlp";
import { getHandler } from "./handlers";
import { SentimentEscalator, type EscalationEvent } from "./escalator";

// ─── Types ─────────────────────────────────────────────────────────

export interface DialogueResult {
  response: string;
  intent: string;
  confidence: number;
  entities: Entity[];
  sentiment: SentimentResult;
  escalated: boolean;
  timestamp: string;
}

// ─── Dialogue Manager ──────────────────────────────────────────────

export class DialogueManager {
  private escalator: SentimentEscalator;

  constructor(escalator?: SentimentEscalator) {
    this.escalator = escalator || new SentimentEscalator();
  }

  /**
   * Process a user message through the full NLP pipeline.
   *
   * Pipeline:
   *   1. Classify intent
   *   2. Extract entities
   *   3. Analyze sentiment
   *   4. Get handler and generate response
   *   5. Check for sentiment escalation
   */
  handle_message(
    userId: string,
    message: string,
    context: Record<string, unknown> = {}
  ): DialogueResult {
    const timestamp = new Date().toISOString();

    // Step 1: Classify intent
    const intentResult = classifyIntent(message);
    const intent = intentResult.intent;
    const confidence = intentResult.confidence;

    // Step 2: Extract entities
    const entities = extractEntities(message);

    // Step 3: Analyze sentiment
    const sentiment = analyzeSentiment(message);

    // Step 4: Get the handler and generate response
    const handler = getHandler(intent);
    const response = handler.handle(message, entities, context);

    // Step 5: Check for sentiment escalation
    const escalated = needsEscalation(message);
    if (escalated) {
      const escalationEvent: EscalationEvent = {
        user_id: userId,
        message,
        sentiment,
        intent,
        timestamp,
        escalation_id: uuidv4(),
      };
      this.escalator.notifyEscalation(escalationEvent);
    }

    const result: DialogueResult = {
      response,
      intent,
      confidence,
      entities,
      sentiment,
      escalated,
      timestamp,
    };

    console.log(
      `[DialogueManager] user=${userId} | intent=${intent} | ` +
        `confidence=${confidence.toFixed(4)} | escalated=${escalated}`
    );

    return result;
  }

  /** Get the escalator instance for adding custom observers. */
  getEscalator(): SentimentEscalator {
    return this.escalator;
  }
}