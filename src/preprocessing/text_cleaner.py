"""spaCy-backed text normalization for resume intelligence."""

from __future__ import annotations

import re
from functools import lru_cache

import nltk
import spacy
from nltk.corpus import stopwords


_FALLBACK_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


@lru_cache(maxsize=1)
def load_nlp():
    """Load a spaCy pipeline, falling back to a blank English model."""

    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        return spacy.blank("en")


@lru_cache(maxsize=1)
def load_stopwords() -> set[str]:
    """Load NLTK stopwords without forcing a runtime download."""

    try:
        return set(stopwords.words("english"))
    except LookupError:
        try:
            nltk.download("stopwords", quiet=True)
            return set(stopwords.words("english"))
        except Exception:
            return _FALLBACK_STOPWORDS


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def clean_text(text: str, *, lemmatize: bool = True) -> str:
    """Clean and normalize text for NLP and vector search."""

    text = (text or "").lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = normalize_whitespace(text)

    nlp = load_nlp()
    stops = load_stopwords()
    doc = nlp(text)

    tokens: list[str] = []
    for token in doc:
        raw = token.text.strip()
        if not raw or raw in stops or len(raw) <= 1:
            continue
        if raw in {"c++", "c#", ".net"}:
            tokens.append(raw)
            continue
        lemma = token.lemma_.strip() if lemmatize and token.lemma_ else raw
        if lemma and lemma not in stops:
            tokens.append(lemma)

    return " ".join(tokens)

