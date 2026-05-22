"""Spanish text normalization for command routing."""

from __future__ import annotations

import re
import unicodedata

_FILLERS = frozenset(
    {
        "por",
        "favor",
        "eh",
        "um",
        "este",
        "esta",
        "pues",
        "bueno",
    }
)


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = strip_accents(text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    words = [w for w in text.split() if w not in _FILLERS]
    return " ".join(words)
