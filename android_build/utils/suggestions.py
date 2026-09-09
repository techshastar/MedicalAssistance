"""
suggestions.py
--------------
One-tap suggestion lines shown under the home / search bars - made for
elders who find typing hard. Each line maps to an `action id` that
`MedicineAssistantApp.run_suggestion()` understands (main.py).

100% offline: these are just fixed strings in English + Hindi.
"""

EN = "en"
HI = "hi"

# (action_id, {"en": line, "hi": line})
SUGGESTIONS = [
    ("tell_my_medicines", {
        "en": "Tell me about my medicines",
        "hi": "मेरी दवाओं के बारे में बताओ",
    }),
    ("check_expiry", {
        "en": "Which medicines are expiring?",
        "hi": "कौन सी दवाएं expire हो रही हैं?",
    }),
    ("storage_tips", {
        "en": "Where should I keep medicines?",
        "hi": "दवाएं कहाँ रखनी चाहिए?",
    }),
    ("add_medicine", {
        "en": "Add a medicine to my cabinet",
        "hi": "मेरी cabinet में दवा जोड़ो",
    }),
    ("family_routine", {
        "en": "Show my family's medicine routine",
        "hi": "परिवार की दवा routine दिखाओ",
    }),
]


def get_suggestions(lang=EN):
    """[(action_id, line_in_language), ...] in a stable, elder-friendly order."""
    lang = HI if lang == HI else EN
    return [(action, texts[lang]) for action, texts in SUGGESTIONS]
