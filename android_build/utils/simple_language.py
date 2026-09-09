"""
simple_language.py  ("Explain Simply" feature - Phase 2)
---------------------------------------------------------
Rule-based simple explanations of medical terms.

IMPORTANT DESIGN RULE: these explanations come from this fixed,
human-written dictionary — NOT from any AI service. Nothing is
generated on the fly, so nothing can be invented.

Phase 7 will add a Hindi layer on top of the same dictionary
(each term will get {"en": ..., "hi": ...}).
"""

import re
from typing import Dict, List, Tuple

# Medical term (lowercase) -> simple everyday explanation, in English & Hindi.
# Keep language at roughly a 10-year-old's reading level.
SIMPLE_EXPLANATIONS: Dict[str, Dict[str, str]] = {
    "non-steroidal anti-inflammatory": {
        "en": "a medicine for pain and swelling (it is NOT a steroid)",
        "hi": "दर्द और सूजन कम करने वाली दवा (यह स्टेरॉइड नहीं है)",
    },
    "nsaid": {
        "en": "a medicine for pain and swelling",
        "hi": "दर्द और सूजन की दवा",
    },
    "analgesic": {
        "en": "a pain-relieving medicine",
        "hi": "दर्द कम करने वाली दवा",
    },
    "antipyretic": {
        "en": "a fever-reducing medicine",
        "hi": "बुखार उतारने वाली दवा",
    },
    "antihistamine": {
        "en": "an anti-allergy medicine",
        "hi": "एलर्जी की दवा",
    },
    "antibiotic": {
        "en": "a medicine that fights bacterial infections (it does NOT work on viruses like cold/flu)",
        "hi": "बैक्टीरिया के infection से लड़ने वाली दवा (जुकाम/flu जैसे virus पर काम नहीं करती)",
    },
    "penicillin": {
        "en": "a common family of antibiotics",
        "hi": "antibiotics का एक प्रचलित परिवार",
    },
    "oral rehydration salts": {
        "en": "a drink mix that replaces water and body salts lost in diarrhoea or vomiting",
        "hi": "दस्त या उल्टी में खोया पानी और नमक पूरा करने वाला घोल",
    },
    "oral rehydration": {
        "en": "replaces water and body salts lost by the body",
        "hi": "शरीर के खोए पानी और नमक की भरपाई करता है",
    },
    "electrolyte": {
        "en": "essential body salts (like sodium and potassium)",
        "hi": "शरीर के ज़रूरी नमक (जैसे sodium, potassium)",
    },
    "dosage form": {
        "en": "the physical form of the medicine (tablet, capsule, syrup, etc.)",
        "hi": "दवा का रूप (tablet, capsule, syrup आदि)",
    },
    "generic name": {
        "en": "the common medical name of the active ingredient",
        "hi": "मुख्य घटक का चिकित्सा नाम",
    },
    "active ingredient": {
        "en": "the main chemical in the medicine that does the work",
        "hi": "दवा का मुख्य घटक जो असली काम करता है",
    },
    "contraindication": {
        "en": "a situation where the medicine should NOT be used",
        "hi": "ऐसी स्थिति जहाँ यह दवा नहीं लेनी चाहिए",
    },
    "drug interaction": {
        "en": "when one medicine changes the effect of another medicine",
        "hi": "जब एक दवा दूसरी दवा का असर बदल दे",
    },
}


def find_simple_explanations(text: str) -> List[Tuple[str, Dict[str, str]]]:
    """
    Scan `text` for known medical terms and return a list of
    (term, explanations_dict) pairs for each term found.

    Longer terms are checked first, so "oral rehydration salts" wins
    over "oral rehydration" if both appear.
    """
    if not text:
        return []

    found: List[Tuple[str, Dict[str, str]]] = []
    lowered = text.lower()
    already_covered = ""

    for term in sorted(SIMPLE_EXPLANATIONS, key=len, reverse=True):
        # \b = word boundary, so "nsaid" does not match inside another word.
        if re.search(r"\b" + re.escape(term) + r"\b", lowered):
            if term not in already_covered:  # skip terms already inside a longer match
                found.append((term, SIMPLE_EXPLANATIONS[term]))
                already_covered += " " + term
    return found


def explain_in_simple_words(text: str, language: str = "en") -> str:
    """
    Return a friendly "In simple words: ..." / "सरल शब्दों में: ..." line
    for the medical terms found in `text`. "" if nothing to explain.
    """
    pairs = find_simple_explanations(text)
    if not pairs:
        return ""
    prefix = "सरल शब्दों में:" if language == "hi" else "In simple words:"
    joined = "; ".join(
        f'"{term}" = {explanations.get(language) or explanations["en"]}'
        for term, explanations in pairs
    )
    return f"{prefix} {joined}."
