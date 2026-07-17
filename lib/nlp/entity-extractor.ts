/**
 * Entity Extractor Module - TypeScript Port
 * Regex-based Named Entity Recognition for banking-relevant entities.
 * Replaces the Python spaCy NER for entity extraction.
 */

export interface Entity {
  text: string;
  label: string;
  start: number;
  end: number;
}

// Regex patterns for banking-relevant entity types
const ENTITY_PATTERNS: { label: string; pattern: RegExp }[] = [
  // Money amounts: £1,250.75 or $500 or 1000 GBP, etc.
  {
    label: "MONEY",
    pattern:
      /(?:£|\$|€)\s?\d[\d,]*\.?\d*|\d[\d,]*\.?\d*\s?(?:GBP|USD|EUR|pounds?|dollars?|euros?)/gi,
  },
  // Dates: 25/12/2024, 2024-01-15, January 15, etc.
  {
    label: "DATE",
    pattern:
      /\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b|\b\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}\b|\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:,?\s+\d{4})?\b/gi,
  },
  // Account numbers: 8-digit numbers (typical UK format)
  {
    label: "ACCOUNT_NUMBER",
    pattern: /\b\d{8}\b/g,
  },
  // Sort codes: 6-digit with optional dashes/dots (12-34-56)
  {
    label: "SORT_CODE",
    pattern: /\b\d{2}[\-\.]?\d{2}[\-\.]?\d{2}\b/g,
  },
  // Card numbers: 16-digit with optional spaces
  {
    label: "CARD_NUMBER",
    pattern: /\b(?:\d{4}\s?){3}\d{4}\b/g,
  },
  // Email addresses
  {
    label: "EMAIL",
    pattern: /\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b/g,
  },
  // Phone numbers (UK format)
  {
    label: "PHONE",
    pattern:
      /\b(?:\+44|0)\s?\d[\d\s\-]{8,12}\d\b/g,
  },
  // Reference numbers: #SR-2024-001, REF123456, etc.
  {
    label: "REFERENCE",
    pattern: /\b(?:#?(?:SR|REF|REF)\-?[\w\-]+)\b/gi,
  },
];

/**
 * Extract named entities from text using regex patterns.
 * Returns all matching entities with their positions.
 */
export function extractEntities(text: string): Entity[] {
  const entities: Entity[] = [];

  for (const { label, pattern } of ENTITY_PATTERNS) {
    // Reset regex lastIndex for each pattern
    const regex = new RegExp(pattern.source, pattern.flags);
    let match: RegExpExecArray | null;

    while ((match = regex.exec(text)) !== null) {
      entities.push({
        text: match[0],
        label,
        start: match.index,
        end: match.index + match[0].length,
      });
    }
  }

  // Sort by position in text
  entities.sort((a, b) => a.start - b.start);

  return entities;
}

/**
 * Extract entities filtered by type.
 */
export function extractEntitiesByType(
  text: string,
  label: string
): Entity[] {
  return extractEntities(text).filter(
    (e) => e.label === label.toUpperCase()
  );
}