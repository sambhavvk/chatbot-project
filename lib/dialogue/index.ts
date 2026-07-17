/**
 * Dialogue Module - Barrel Export
 */

export { DialogueManager, type DialogueResult } from "./manager";
export { getHandler, registerHandler, type IntentHandler } from "./handlers";
export { SentimentEscalator, type EscalationEvent, type SentimentObserver } from "./escalator";