"""
search.py
---------
Medicine search (Phase 1) + OCR-text matching (Phase 3)
+ fuzzy typo tolerance (Phase 4).

Match types:
    EXACT    -> normalized query EQUALS a name/brand/generic, or a full
                name appears inside the scanned text
    POSSIBLE -> weaker evidence: partial text, scattered words, or a
                FUZZY (spelling-mistake) match. Always shown as
                "possible match - please confirm with the packaging".

Safety design:
  * Blank/empty queries return nothing.
  * Unknown names return an empty list — the app NEVER guesses.
  * Fuzzy matches can only ever be POSSIBLE, never EXACT.
"""

import sqlite3
from dataclasses import dataclass
from typing import List, Optional

from database.database import fetch_all_medicines
from database.models import Medicine
from medicine.matcher import best_fuzzy_score, DEFAULT_THRESHOLD, _meaningful_tokens
from utils.text_cleaner import normalize_text

EXACT = "exact"
POSSIBLE = "possible"


@dataclass
class SearchMatch:
    """
    One search result: the medicine, HOW confidently it matched,
    and (for fuzzy matches) the similarity score 0-1.
    """
    medicine: Medicine
    match_type: str                     # EXACT or POSSIBLE
    score: Optional[float] = None       # only set for fuzzy matches


def _searchable_names(medicine: Medicine) -> List[str]:
    """All normalized names a medicine can be searched by."""
    raw_names = [
        medicine.medicine_name,
        medicine.brand_name,
        medicine.generic_name,
        medicine.active_ingredient,
    ]
    return [normalize_text(name) for name in raw_names if name]


def _sort_results(exact, possible):
    """Exact first; then plain possible matches; fuzzy ones by score."""
    exact.sort(key=lambda m: m.medicine.medicine_name.lower())
    possible.sort(key=lambda m: (
        m.score is not None,                    # non-fuzzy possible first
        -(m.score or 0),                        # best fuzzy score next
        m.medicine.medicine_name.lower(),
    ))
    return exact + possible


def search_medicines(
    connection: sqlite3.Connection,
    query: str,
    fuzzy: bool = True,
    fuzzy_threshold: float = DEFAULT_THRESHOLD,
) -> List[SearchMatch]:
    """
    Search the database for `query`.

    With fuzzy=True (default, Phase 4), small spelling mistakes also
    match - but ONLY as POSSIBLE matches carrying a similarity score.
    Returns [] for empty or unknown queries — never a wild guess.
    """
    normalized_query = normalize_text(query)
    if not normalized_query:
        return []

    # Words with no identification value (e.g. the "demo"/"example"
    # metadata in the development dataset) can never BE a search hit.
    from medicine.matcher import _IGNORED_TOKENS
    if normalized_query in _IGNORED_TOKENS:
        return []

    exact_matches: List[SearchMatch] = []
    possible_matches: List[SearchMatch] = []

    for medicine in fetch_all_medicines(connection):
        names = _searchable_names(medicine)

        if normalized_query in names:
            exact_matches.append(SearchMatch(medicine, EXACT))
        elif any(normalized_query in name for name in names):
            possible_matches.append(SearchMatch(medicine, POSSIBLE))
        elif fuzzy:
            # Phase 4: no direct hit - try fuzzy (typo-tolerant) matching.
            score = best_fuzzy_score(normalized_query, names)
            if score >= fuzzy_threshold:
                # ALWAYS possible - fuzzy can never promote itself to EXACT.
                possible_matches.append(
                    SearchMatch(medicine, POSSIBLE, round(score, 2))
                )

    return _sort_results(exact_matches, possible_matches)


def find_medicines_in_ocr_text(
    connection: sqlite3.Connection,
    raw_text: str,
    fuzzy: bool = True,
    fuzzy_threshold: float = 0.80,
) -> List[SearchMatch]:
    """
    Phase 3 (+4) : find which known medicines are mentioned in OCR text.

      * EXACT    -> a full normalized name/brand/generic appears in the text
      * POSSIBLE -> every meaningful word of a name appears in the text,
                    or (Phase 4) a near-identical word does
                    (e.g. OCR read "paracetamo1" instead of "paracetamol")

    The fuzzy threshold is higher here (0.80) because OCR noise should
    make us MORE careful, not less. Result is still only "possible".
    """
    normalized_text = normalize_text(raw_text)
    if not normalized_text:
        return []

    text_tokens = set(normalized_text.split())
    meaningful_text_tokens = set(_meaningful_tokens(normalized_text))
    exact_matches: List[SearchMatch] = []
    possible_matches: List[SearchMatch] = []

    for medicine in fetch_all_medicines(connection):
        names = _searchable_names(medicine)

        if any(name and name in normalized_text for name in names):
            exact_matches.append(SearchMatch(medicine, EXACT))
            continue

        def all_tokens_present(name: str) -> bool:
            meaningful = [
                token for token in name.split()
                if len(token) >= 4 and not token.isdigit()
            ]
            return bool(meaningful) and all(
                token in text_tokens for token in meaningful
            )

        if any(all_tokens_present(name) for name in names):
            possible_matches.append(SearchMatch(medicine, POSSIBLE))
        elif fuzzy:
            # Phase 4: OCR misread a word? ("paracetamo1" vs "paracetamol")
            name_tokens = {
                token for name in names for token in _meaningful_tokens(name)
            }
            best = 0.0
            for n_token in name_tokens:
                for t_token in meaningful_text_tokens:
                    best = max(best, best_fuzzy_score(t_token, [n_token]))
            if best >= fuzzy_threshold:
                possible_matches.append(
                    SearchMatch(medicine, POSSIBLE, round(best, 2))
                )

    return _sort_results(exact_matches, possible_matches)
