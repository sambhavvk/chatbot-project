/**
 * Intent Classifier Module - TypeScript Port
 * Strategy Pattern: classifies user messages into banking intents.
 * Uses keyword-based matching with scoring (equivalent to MockIntentClassifier).
 * Can be swapped with @xenova/transformers zero-shot classification for higher accuracy.
 */

export interface IntentResult {
  intent: string;
  confidence: number;
}

// Banking intent keywords mapped to intent names
// Mirrors the Python MockIntentClassifier and banking77 dataset categories
const INTENT_KEYWORDS: Record<string, string[]> = {
  balance: [
    "balance", "money", "account", "how much", "funds", "available",
    "current balance", "savings", "checking", "overdraft", "statement",
  ],
  transaction: [
    "transfer", "send", "payment", "pay", "transaction", "wire",
    "move money", "send money", "direct debit", "standing order", "bacs",
  ],
  card: [
    "card", "credit", "debit", "atm", "pin", "chip", "contactless",
    "lost card", "stolen card", "replacement", "block card", "freeze",
    "activate card", "new card", "virtual card",
  ],
  loan: [
    "loan", "mortgage", "borrow", "repayment", "interest rate",
    "apr", "monthly payment", "borrowing", "lending", "overdraft limit",
  ],
  complaint: [
    "complaint", "issue", "problem", "unhappy", "wrong", "error",
    "disappointed", "frustrated", "angry", "terrible", "awful",
    "disgusting", "unacceptable", "ridiculous", "scam",
  ],
  greeting: [
    "hello", "hi", "hey", "good morning", "good afternoon",
    "good evening", "howdy", "greetings", "what's up",
  ],
  goodbye: [
    "bye", "goodbye", "see you", "take care", "cheers",
    "thanks bye", "that's all", "nothing else",
  ],
  account: [
    "open account", "close account", "account details", "update details",
    "change address", "personal details", "kyc", "verification",
    "identity", "proof of address",
  ],
};

/**
 * Classify the intent of a user message using keyword scoring.
 * Returns the best matching intent with a confidence score.
 */
export function classifyIntent(text: string): IntentResult {
  const textLower = text.toLowerCase().trim();
  let bestIntent = "unknown";
  let bestScore = 0;

  for (const [intent, keywords] of Object.entries(INTENT_KEYWORDS)) {
    let score = 0;
    for (const keyword of keywords) {
      if (textLower.includes(keyword)) {
        // Longer keyword matches get higher weight
        score += keyword.split(" ").length;
      }
    }
    if (score > bestScore) {
      bestScore = score;
      bestIntent = intent;
    }
  }

  // Normalize confidence to 0-1 range
  const confidence = Math.min(bestScore / 3, 1);

  return {
    intent: bestIntent,
    confidence: Math.round(confidence * 10000) / 10000,
  };
}