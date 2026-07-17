/**
 * Sentiment Escalator - TypeScript Port
 * Observer Pattern: listens for negative sentiment events and triggers escalation actions.
 * Replaces the Python SentimentEscalator.
 */

export interface EscalationEvent {
  user_id: string;
  message: string;
  sentiment: {
    neg: number;
    neu: number;
    pos: number;
    compound: number;
  };
  intent: string;
  timestamp: string;
  escalation_id: string;
}

// ─── Observer Interface ────────────────────────────────────────────

export type SentimentObserver = (event: EscalationEvent) => void;

// ─── Logging Observer ──────────────────────────────────────────────

function loggingObserver(event: EscalationEvent): void {
  console.warn(
    `[ESCALATION] User ${event.user_id} | ` +
      `compound=${event.sentiment.compound.toFixed(4)} | ` +
      `message="${event.message}"`
  );
}

// ─── Escalator Class ──────────────────────────────────────────────

export class SentimentEscalator {
  private observers: SentimentObserver[] = [];

  constructor(addDefaultObserver: boolean = true) {
    if (addDefaultObserver) {
      this.observers.push(loggingObserver);
    }
  }

  /** Register an additional observer. */
  addObserver(observer: SentimentObserver): void {
    this.observers.push(observer);
  }

  /** Remove a previously registered observer. */
  removeObserver(observer: SentimentObserver): void {
    const index = this.observers.indexOf(observer);
    if (index !== -1) {
      this.observers.splice(index, 1);
    }
  }

  /** Notify all registered observers of an escalation event. */
  notifyEscalation(event: EscalationEvent): void {
    for (const observer of this.observers) {
      try {
        observer(event);
      } catch (error) {
        console.error("Error in escalation observer:", error);
      }
    }
  }
}