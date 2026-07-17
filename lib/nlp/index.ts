/**
 * NLP Module - Barrel Export
 * Centralises all NLP functions for clean imports.
 */

export { classifyIntent, type IntentResult } from "./intent-classifier";
export { analyzeSentiment, needsEscalation, type SentimentResult } from "./sentiment-analyzer";
export { extractEntities, extractEntitiesByType, type Entity } from "./entity-extractor";