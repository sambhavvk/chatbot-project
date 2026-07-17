/**
 * Intent Handlers - TypeScript Port
 * Factory Pattern: each handler generates a contextual response for a specific intent.
 * Replaces the Python handler registry and factory.
 */

import type { Entity } from "@/lib/nlp";

// ─── Handler Interface ─────────────────────────────────────────────

export interface IntentHandler {
  intentName: string;
  handle(
    userMessage: string,
    entities: Entity[],
    context: Record<string, unknown>
  ): string;
}

// ─── Concrete Handlers ─────────────────────────────────────────────

class BalanceHandler implements IntentHandler {
  intentName = "balance";

  handle(
    _userMessage: string,
    _entities: Entity[],
    context: Record<string, unknown>
  ): string {
    const accountName = (context.account_name as string) || "your account";
    const balance = (context.balance as string) || "£1,250.75";
    return (
      `The current balance for ${accountName} is ${balance}. ` +
      "Is there anything else I can help you with?"
    );
  }
}

class TransactionHandler implements IntentHandler {
  intentName = "transaction";

  handle(
    _userMessage: string,
    entities: Entity[],
    _context: Record<string, unknown>
  ): string {
    const moneyEntities = entities
      .filter((e) => e.label === "MONEY")
      .map((e) => e.text);

    if (moneyEntities.length > 0) {
      const amount = moneyEntities[0];
      return (
        `I can help you transfer ${amount}. ` +
        "To proceed, I'll need the recipient's sort code and account number. " +
        "Would you like to continue?"
      );
    }

    return (
      "I'd be happy to help with a transaction. " +
      "Could you tell me the amount and the recipient's details?"
    );
  }
}

class CardHandler implements IntentHandler {
  intentName = "card";

  handle(
    userMessage: string,
    _entities: Entity[],
    _context: Record<string, unknown>
  ): string {
    const msgLower = userMessage.toLowerCase();
    const lostKeywords = ["lost", "stolen", "missing", "block"];

    if (lostKeywords.some((kw) => msgLower.includes(kw))) {
      return (
        "I'm sorry to hear your card is missing. For your security, " +
        "I can immediately block your card and arrange a replacement. " +
        "Would you like me to proceed with this?"
      );
    }

    return (
      "I can help with card-related services including reporting a lost card, " +
      "ordering a replacement, or checking your card details. " +
      "What would you like to do?"
    );
  }
}

class LoanHandler implements IntentHandler {
  intentName = "loan";

  handle(): string {
    return (
      "I can provide information about our loan and mortgage products. " +
      "Our current personal loan rates start from 5.9% APR. " +
      "Would you like me to connect you with a loan specialist, " +
      "or would you prefer to browse our options online?"
    );
  }
}

class ComplaintHandler implements IntentHandler {
  intentName = "complaint";

  handle(): string {
    const date = new Date().toISOString().split("T")[0];
    const random = Math.random().toString(36).substring(2, 6).toUpperCase();
    return (
      "I understand you're experiencing an issue, and I want to help resolve it. " +
      "I've logged your complaint and escalated it to our support team. " +
      "A representative will review your case and get back to you within 24 hours. " +
      `Your reference number is #SR-${date}-${random}. ` +
      "Is there anything else I can assist you with in the meantime?"
    );
  }
}

class GreetingHandler implements IntentHandler {
  intentName = "greeting";

  handle(
    _userMessage: string,
    _entities: Entity[],
    context: Record<string, unknown>
  ): string {
    const userName = (context.user_name as string) || "there";
    return (
      `Hello ${userName}! Welcome to our virtual assistant. ` +
      "I can help with balance inquiries, transactions, card services, " +
      "loans, and more. How can I assist you today?"
    );
  }
}

class GoodbyeHandler implements IntentHandler {
  intentName = "goodbye";

  handle(): string {
    return (
      "Thank you for chatting with us today! " +
      "If you need further assistance, don't hesitate to reach out. " +
      "Have a great day!"
    );
  }
}

class AccountHandler implements IntentHandler {
  intentName = "account";

  handle(): string {
    return (
      "I can help you with account-related queries. " +
      "For security, I'll need to verify your identity. " +
      "Could you please provide your account number or the email " +
      "associated with your account?"
    );
  }
}

class FallbackHandler implements IntentHandler {
  intentName = "fallback";

  handle(): string {
    return (
      "I'm not quite sure I understood that. Could you rephrase your request? " +
      "I can help with balance checks, transactions, card services, loans, " +
      "and account-related questions."
    );
  }
}

// ─── Handler Registry (Factory Pattern) ────────────────────────────

const HANDLER_REGISTRY: Map<string, IntentHandler> = new Map();

// Register all handlers
const handlers: IntentHandler[] = [
  new BalanceHandler(),
  new TransactionHandler(),
  new CardHandler(),
  new LoanHandler(),
  new ComplaintHandler(),
  new GreetingHandler(),
  new GoodbyeHandler(),
  new AccountHandler(),
];

for (const handler of handlers) {
  HANDLER_REGISTRY.set(handler.intentName, handler);
}

const fallbackHandler = new FallbackHandler();

/**
 * Get the appropriate handler for an intent.
 * Falls back to FallbackHandler for unknown intents.
 */
export function getHandler(intent: string): IntentHandler {
  return HANDLER_REGISTRY.get(intent) || fallbackHandler;
}

/**
 * Register a custom handler for a new intent.
 */
export function registerHandler(handler: IntentHandler): void {
  HANDLER_REGISTRY.set(handler.intentName, handler);
}