/**
 * Sentiment Analyzer Module - TypeScript Port
 * Uses the 'sentiment' npm package (AFINN-based) for lightweight sentiment scoring.
 * Replaces the Python VADER SentimentIntensityAnalyzer.
 */

import Sentiment from "sentiment";

const sentimentAnalyzer = new Sentiment();

export interface SentimentResult {
  neg: number;
  neu: number;
  pos: number;
  compound: number;
}

// Escalation threshold: compound score below this triggers escalation
const DEFAULT_ESCALATION_THRESHOLD = -0.3;

/**
 * Analyze sentiment of a text string.
 * Returns normalized scores matching the Python VADER output format.
 */
export function analyzeSentiment(text: string): SentimentResult {
  const result = sentimentAnalyzer.analyze(text);

  // The 'sentiment' npm package gives: score, comparative, positive[], negative[]
  // We normalize to match VADER's neg/neu/pos/compound format
  const comparative = result.comparative;

  // Map comparative score (-5 to +5 range) to compound (-1 to +1)
  const compound = Math.max(-1, Math.min(1, comparative / 2));

  // Approximate neg/neu/pos from the word-level analysis
  const posWords = result.positive.length;
  const negWords = result.negative.length;
  const totalWords = result.tokens.length || 1;

  const neg = Math.round((negWords / totalWords) * 10000) / 10000;
  const pos = Math.round((posWords / totalWords) * 10000) / 10000;
  const neu = Math.round((1 - neg - pos) * 10000) / 10000;

  return {
    neg: Math.max(0, neg),
    neu: Math.max(0, Math.min(1, neu)),
    pos: Math.max(0, pos),
    compound: Math.round(compound * 10000) / 10000,
  };
}

/**
 * Check if sentiment is negative enough to warrant escalation.
 */
export function needsEscalation(
  text: string,
  threshold: number = DEFAULT_ESCALATION_THRESHOLD
): boolean {
  const scores = analyzeSentiment(text);
  return scores.compound < threshold;
}