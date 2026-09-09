"""
matcher.py  (Phase 4 - fuzzy medicine-name matching)
------------------------------------------------------
Handles small spelling mistakes like "paracitamol" or "dolo 65o".

⚠️ SAFETY-FIRST DESIGN (required by the project spec):
    Fuzzy matching produces "possible match" results ONLY.
    It can NEVER turn a typo into an EXACT/confident match.
    Every fuzzy result carries a similarity score (0-1) so the
    user can judge for themselves, and the UI always says
    "please confirm with the packaging".

How the score works:
    We compare the query against a medicine's names in 3 ways
    and keep the best similarity:
      1. whole query vs whole name        ("dolo 65o" vs "dolo 650")
      2. whole query vs name's word-part  ("paracitamol" vs "paracetamol")
      3. each query WORD vs each name word ("crocim" vs "crocin")

    Numbers-only tokens ("500", "650") are never used alone, so a
    strength printed anywhere can never trigger a match by itself.

Uses only Python's standard library (difflib) - nothing to install.
"""

import re
from difflib import SequenceMatcher
from typing import Iterable, List

from utils.text_cleaner import normalize_text

# Below this similarity we say nothing at all; above it we say
# "possible match" (never more). 0.72 is deliberately conservative.
DEFAULT_THRESHOLD = 0.72

# Words shorter than this are too unreliable to fuzzy-match.
MIN_TOKEN_LENGTH = 4

# Tokens are clean alphanumeric WORDS (punctuation never sticks to them).
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

# Words that carry no identification value and must never drive a match.
# ("demo"/"example" appear in the development dataset's brand labels like
#  "Crocin 500 (demo example)" - they are metadata, not medicine names.)
_IGNORED_TOKENS = {"demo", "example"}


def similarity(a: str, b: str) -> float:
    """
    Similarity between two texts, from 0.0 (totally different)
    to 1.0 (identical). Case and extra spaces are ignored.
    """
    na, nb = normalize_text(a), normalize_text(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def _meaningful_tokens(text: str) -> List[str]:
    """
    Tokens worth matching:
      * clean words ([a-z0-9]+) - punctuation never sticks to them,
        so "(demo" cannot exist as a token
      * at least MIN_TOKEN_LENGTH characters
      * containing a letter (pure numbers like "500" are excluded,
        so a strength printed on any strip can never match by itself)
      * not in the ignored list (metadata words like "demo"/"example")
    """
    return [
        token
        for token in _TOKEN_PATTERN.findall(normalize_text(text))
        if len(token) >= MIN_TOKEN_LENGTH
        and any(ch.isalpha() for ch in token)
        and token not in _IGNORED_TOKENS
    ]


def _word_part(name: str) -> str:
    """A name stripped down to only its letter-words: "dolo 650" -> "dolo"."""
    return " ".join(
        token for token in normalize_text(name).split()
        if any(ch.isalpha() for ch in token)
    )


def best_fuzzy_score(query: str, candidate_names: Iterable[str]) -> float:
    """
    Best similarity (0-1) between `query` and any of a medicine's names.
    Returns 0.0 when there is nothing sensible to compare.
    """
    normalized_query = normalize_text(query)
    if not normalized_query:
        return 0.0
    # RULE: a query with no letter in it (e.g. just "500") can never
    # fuzzy-match a medicine name - strengths are not identifiers.
    if not any(ch.isalpha() for ch in normalized_query):
        return 0.0

    query_tokens = _meaningful_tokens(normalized_query)
    best = 0.0

    for name in candidate_names:
        normalized_name = normalize_text(name)
        if not normalized_name:
            continue

        # 1) whole query vs whole name
        best = max(best, similarity(normalized_query, normalized_name))

        # 2) whole query vs the name's word-part
        word_part = _word_part(normalized_name)
        if word_part and word_part != normalized_name:
            best = max(best, similarity(normalized_query, word_part))

        # 3) word-by-word comparison (handles typos inside one word)
        name_tokens = _meaningful_tokens(normalized_name)
        for q_token in query_tokens:
            for n_token in name_tokens:
                best = max(best, similarity(q_token, n_token))

    return best
