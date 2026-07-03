"""
Entity Extractor Module - Wrapper around spaCy for Named Entity Recognition.
Extracts entities like names, dates, amounts, card types, etc. from user messages.
"""

from typing import List, Dict, Any, Optional
import spacy


class EntityExtractor:
    """
    Wraps a spaCy NLP pipeline for entity extraction.
    Designed to be dependency-injected into DialogueManager.
    """

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        """
        Args:
            model_name: spaCy model to load (default: small English model).
        """
        try:
            self._nlp = spacy.load(model_name)
        except OSError:
            raise OSError(
                f"spaCy model '{model_name}' not found. "
                "Install it with: python -m spacy download {model_name}"
            )
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text.

        Args:
            text: Raw user message.

        Returns:
            List of entity dicts with keys: 'text', 'label', 'start', 'end'.
        """
        doc = self._nlp(text)
        entities = [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            for ent in doc.ents
        ]
        return entities

    def extract_by_type(
        self, text: str, entity_type: str
    ) -> List[Dict[str, Any]]:
        """
        Extract entities of a specific type (e.g., 'MONEY', 'DATE', 'PERSON').

        Args:
            text: Raw user message.
            entity_type: spaCy entity label (e.g., 'MONEY', 'DATE').

        Returns:
            Filtered list of entity dicts.
        """
        all_entities = self.extract(text)
        return [e for e in all_entities if e["label"] == entity_type]