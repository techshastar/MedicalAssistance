"""
text_cleaner.py
---------------
Small, reusable text-cleaning helpers.

Phase 1 use: normalizing medicine names so that
    "Paracetamol"  ==  "paracetamol"  ==  "  PARACETAMOL   "
Later phases (OCR) will add more aggressive cleaning here.
"""

import re

# Pre-compiled pattern for "one or more whitespace characters".
_WHITESPACE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """
    Return a normalized version of `text` for safe comparison.

    Rules:
      1. Convert to lowercase          -> "PARACETAMOL" -> "paracetamol"
      2. Remove leading/trailing space -> "  dolo 650 " -> "dolo 650"
      3. Collapse repeated inner space -> "dolo   650"  -> "dolo 650"

    Note: we intentionally do NOT remove characters or 'fix' spelling here.
    Spelling tolerance (fuzzy matching) is a Phase 4 feature and must stay
    clearly labelled as "possible match" — never a confident guess.
    """
    if text is None:
        return ""
    return _WHITESPACE.sub(" ", str(text)).strip().lower()


# Anything that is not a letter/number/useful symbol -> removed (OCR specks).
_OCR_JUNK = re.compile(r"[^a-z0-9\s.,%]")
# Separators OCR often puts inside words/names: "Dolo-650", "EXP:12/26".
_OCR_SEPARATORS = re.compile(r"[\-/_:;|~`'\"()\[\]{}*#@!$^&+=<>?\\]")


def clean_ocr_text(text: str) -> str:
    """
    Clean raw OCR output (Phase 3) before matching it against the database.

    OCR text is messy: random specks, broken characters, stray separators.
    Steps:
      1. lowercase
      2. turn separators ("-", "/", ":", newlines...) into spaces,
         so "Dolo-650" becomes "dolo 650" and matches the database name
      3. remove leftover junk symbols (random OCR specks)
      4. collapse repeated whitespace
    """
    if not text:
        return ""
    cleaned = _OCR_SEPARATORS.sub(" ", str(text).lower())
    cleaned = _OCR_JUNK.sub(" ", cleaned)
    return _WHITESPACE.sub(" ", cleaned).strip()
