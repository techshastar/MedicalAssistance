"""
information.py  (Phases 2, 5, 6, 7)
-----------------------------------
Turns ONE Medicine object into:
    * the full DETAILS PAGE          (Phase 2) - now in English AND Hindi
    * the PACKAGING section          (Phase 5) - now in English AND Hindi
    * the SPOKEN SUMMARY for Listen  (Phase 6) - now in English AND Hindi

Golden rules enforced here:
  * Missing data is shown as "Not available in the database." - never invented.
  * Serious warnings are clearly marked as warnings.
  * General information is always separated from the doctor/pharmacist's
    instructions.
  * An unreadable expiry produces the honest "could not be detected"
    message - never an estimate.
"""

import re
from typing import List, Optional, Tuple

from database.models import Medicine
from medicine.search import EXACT
from utils.date_utils import (
    PackagingInfo,
    NO_EXPIRY_MESSAGE,
    EXPIRING_SOON_DAYS,
    EXPIRED,
    EXPIRING_SOON,
)
from utils.languages import t, EN, HI
from utils.simple_language import explain_in_simple_words

NOT_AVAILABLE = "Not available in the database."
LINE = "=" * 62
THIN_LINE = "-" * 62

# Explanation levels (Settings > Explanation level).
# Simple  -> short page, easy words, safety lines are NEVER dropped
# Normal  -> the full standard page
# Detailed-> normal page + who-can-take + storage cards inside the page itself
LV_SIMPLE = "simple"
LV_NORMAL = "normal"
LV_DETAILED = "detailed"
EXPLANATION_LEVELS = (LV_SIMPLE, LV_NORMAL, LV_DETAILED)

DISCLAIMER = (
    "This application provides general medicine information for educational "
    "purposes only. It does not replace advice from a qualified doctor or "
    "pharmacist. Always check the medicine packaging and follow your "
    "healthcare professional's instructions."
)
DISCLAIMER_HI = (
    "यह ऐप केवल सामान्य, शैक्षिक दवा-जानकारी देता है। यह किसी योग्य डॉक्टर या "
    "फार्मासिस्ट की सलाह का विकल्प नहीं है। हमेशा दवा के packet की जानकारी "
    "जाँचें और अपने चिकित्सक के निर्देशों का पालन करें।"
)
URGENT_NOTE = (
    "For urgent symptoms, suspected overdose, or poisoning, seek immediate "
    "medical help. Do not rely on this application in an emergency."
)
URGENT_NOTE_HI = (
    "गंभीर लक्षण, overdose या poison के शक पर तुरंत चिकित्सा सहायता लें। "
    "आपात स्थिति में इस ऐप पर निर्भर न रहें।"
)

# Warning fields in fixed display order, mapped to language keys.
WARNING_FIELDS: List[Tuple[str, str]] = [
    ("pregnancy_warning", "warn_pregnancy"),
    ("breastfeeding_warning", "warn_breastfeeding"),
    ("children_warning", "warn_children"),
    ("elderly_warning", "warn_elderly"),
    ("kidney_warning", "warn_kidney"),
    ("liver_warning", "warn_liver"),
    ("drug_interactions", "warn_drugs"),
    ("food_interactions", "warn_food"),
]


def _na(lang: str) -> str:
    """'Not available' in the current language."""
    return t("not_available", lang) if lang == HI else NOT_AVAILABLE


def _confidence_line(match_type: Optional[str], lang: str) -> str:
    """Human-readable identification confidence."""
    if match_type is None:
        return t("conf_manual", lang)
    if match_type == EXACT:
        return t("conf_exact", lang)
    return t("conf_possible", lang)


def format_details_page(
    medicine: Medicine,
    match_type: Optional[str] = EXACT,
    language: str = EN,
    level: str = LV_NORMAL,
) -> str:
    """
    Build the details page (English or Hindi) as one printable string.

    `level` picks how much the page explains:
      LV_SIMPLE   -> short, elder-friendly page (safety never removed)
      LV_NORMAL   -> the full standard page
      LV_DETAILED -> normal page + who-can-take + storage sections
    """
    if level == LV_SIMPLE:
        return _format_simple_page(medicine, match_type, language)
    page = _format_normal_page(medicine, match_type, language)
    if level == LV_DETAILED:
        extra = [
            "",
            f">> {t('who_card', language)}",
            THIN_LINE,
            format_age_suitability(medicine, language),
            "",
            f">> {t('storage_card', language)}",
            THIN_LINE,
            format_storage_card(medicine, language),
        ]
        # keep the two cards BEFORE the trailing disclaimer block:
        marker = LINE + "\n" + f"  {t('disclaimer_lbl', language)}"
        if marker in page:
            head, tail = page.split(marker, 1)
            page = head + "\n".join(extra) + "\n\n" + marker + tail
        else:
            page = page + "\n" + "\n".join(extra)
    return page


def _format_normal_page(
    medicine: Medicine,
    match_type: Optional[str] = EXACT,
    language: str = EN,
) -> str:
    """Build the full standard details page (English or Hindi)."""
    out: List[str] = []
    add = out.append
    na = _na(language)

    # ---------------- Header: name + confidence + source ----------------
    add(LINE)
    add(f"  {medicine.medicine_name}")
    add(LINE)
    add(f"  {_confidence_line(match_type, language)}")
    add(f"  {t('generic_lbl', language)} : {medicine.generic_name or na}")
    add(f"  {t('strength_lbl', language)} : {medicine.strength or na}")
    add(f"  {t('form_lbl', language)} : {medicine.dosage_form or na}")
    add(f"  {t('manufacturer_lbl', language)} : {medicine.manufacturer or na}")
    if medicine.is_demo_data():
        add(f"  {t('demo_source', language)}")
    elif medicine.source:
        add(f"  [Source: {medicine.source} | last updated: {medicine.last_updated or 'unknown'}]")

    # ------------- Section 1: What is this medicine? (Explain Simply) ---
    add("")
    add(f">> {t('what_is', language)}")
    add(THIN_LINE)
    if medicine.general_usage:
        add(f"  {medicine.general_usage}")
    elif medicine.category:
        add(f"  {t('official_category', language)}: {medicine.category}")
    else:
        add(f"  {na}")
    if medicine.category:
        add(f"  {t('official_category', language)}: {medicine.category}")
        simple = explain_in_simple_words(medicine.category, language)
        if simple:
            add(f"  {simple}")   # <- the "Explain Simply" feature

    # ------------------- Section 2: What is it used for? ----------------
    add("")
    add(f">> {t('uses_hdr', language)}")
    add(THIN_LINE)
    uses = medicine.uses_list()
    if uses:
        for use in uses:
            add(f"  - {use}")
    else:
        add(f"  {na}")

    # ---------------- Section 3: How is it generally taken? -------------
    add("")
    add(f">> {t('how_taken', language)}")
    add(THIN_LINE)
    add(f"  {medicine.administration or na}")
    add("")
    for line in t("general_note", language).split("\n"):
        add(f"  {line}")
    if medicine.storage_information:
        add(f"  {t('storage_lbl', language)}: {medicine.storage_information}")

    # ------------------- Section 4: Safety & warnings -------------------
    add("")
    add(f">> {t('safety_hdr', language)}")
    add(THIN_LINE)
    any_warning = False
    for field_name, label_key in WARNING_FIELDS:
        value = getattr(medicine, field_name, None)
        if value:
            add(f"  * {t(label_key, language)}: {value}")
            any_warning = True
    if not any_warning:
        add(f"  {na}")

    # ----------------------- Section 5: Side effects --------------------
    add("")
    add(f">> {t('side_fx_hdr', language)}")
    add(THIN_LINE)
    effects = medicine.side_effects_list()
    if effects:
        add(f"  {t('common_fx', language)}")
        for effect in effects:
            add(f"    - {effect}")
    else:
        add(f"  {na}")
    add("")
    add(f"  {t('serious_signs', language)}")
    add(f"     {medicine.serious_warnings or na}")

    # --------------------------- Disclaimer -----------------------------
    disclaimer = DISCLAIMER_HI if language == HI else DISCLAIMER
    urgent = URGENT_NOTE_HI if language == HI else URGENT_NOTE
    add("")
    add(LINE)
    add(f"  {t('disclaimer_lbl', language)}: {disclaimer}")
    add(f"  {urgent}")
    add(LINE)

    return "\n".join(out)


def format_packaging_info_section(
    info: PackagingInfo,
    today=None,
    language: str = EN,
) -> str:
    """
    Phase 5 (+7): MFG / EXP / batch section with expiry status,
    in English or Hindi. The safety behaviour never changes:
    no readable expiry -> honest "could not be detected" message;
    "NOT EXPIRED" never claims "safe".
    """
    from datetime import date as _date
    today = today or _date.today()

    out: List[str] = []
    add = out.append

    add("")
    add(f">> {t('pkg_hdr', language)}")
    add(THIN_LINE)
    month_tag = t("month_printed", language)
    if info.batch_number:
        add(f"  {t('batch_lbl', language)} : {info.batch_number}")
    if info.mfg_raw:
        suffix = f"  {month_tag}" if info.mfg_month_only else ""
        add(f"  {t('mfg_lbl', language)} : {info.mfg_raw}{suffix}")

    if info.expiry_raw:
        suffix = f"  {month_tag}" if info.expiry_month_only else ""
        add(f"  {t('exp_lbl', language)} : {info.expiry_raw}{suffix}")
        status = info.expiry_status(today)
        if status == EXPIRED:
            add(f"  {t('status_lbl', language)} : {t('status_expired', language)}")
            for line in t("expired_advice", language).split("\n"):
                add(f"                           {line.strip()}")
        elif status == EXPIRING_SOON:
            soon_text = t("status_soon", language, n=EXPIRING_SOON_DAYS)
            for i, line in enumerate(soon_text.split("\n")):
                add(f"  {t('status_lbl', language)} : {line.strip()}" if i == 0
                    else f"                           {line.strip()}")
            add(f"                           {t('soon_advice', language)}")
        else:
            add(f"  {t('status_lbl', language)} : {t('status_valid', language)}")
        if info.expiry_month_only:
            for line in t("month_convention", language).split("\n"):
                add(f"  {line}")
    else:
        message = t("no_expiry", language) if language == HI else NO_EXPIRY_MESSAGE
        add(f"  {message}")

    if not (info.batch_number or info.mfg_raw or info.expiry_raw):
        for line in t("no_pkg_details", language).split("\n"):
            add(f"  {line}")

    add("")
    for line in t("ocr_verify", language).split("\n"):
        add(f"  {line}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Phase 6/7: spoken summary for the "Listen" feature (English & Hindi)
# ---------------------------------------------------------------------------
def _speakable_strength(strength: Optional[str], language: str = EN) -> str:
    """Make a strength easy to SAY: '500 mg' -> '500 milligrams' / '500 मिलीग्राम'."""
    if not strength:
        return ""
    text = str(strength)
    if language == HI:
        text = re.sub(r"(\d+(?:\.\d+)?)\s*mg\b", r"\1 मिलीग्राम", text, flags=re.I)
        text = re.sub(r"(\d+(?:\.\d+)?)\s*mcg\b", r"\1 माइक्रोग्राम", text, flags=re.I)
        text = re.sub(r"(\d+(?:\.\d+)?)\s*ml\b", r"\1 मिलीलीटर", text, flags=re.I)
    else:
        text = re.sub(r"(\d+(?:\.\d+)?)\s*mg\b", r"\1 milligrams", text, flags=re.I)
        text = re.sub(r"(\d+(?:\.\d+)?)\s*mcg\b", r"\1 micrograms", text, flags=re.I)
        text = re.sub(r"(\d+(?:\.\d+)?)\s*ml\b", r"\1 millilitres", text, flags=re.I)
    return text.replace("%", " percent")


def build_spoken_summary(
    medicine: Medicine,
    packaging: Optional[PackagingInfo] = None,
    match_type: str = EXACT,
    language: str = EN,
) -> str:
    """
    Short summary read aloud by "Listen" - name, uses, main precautions,
    administration, and expiry status, then a safety closing.
    Available in English ("en") and Hindi ("hi").
    """
    sentences: List[str] = []
    strength = _speakable_strength(medicine.strength, language)
    uses = medicine.uses_list()

    if language == HI:
        # ------------------------- Hindi version -------------------------
        if strength and strength.split()[0] not in medicine.medicine_name:
            sentences.append(f"यह दवा {medicine.medicine_name} है, मात्रा {strength}।")
        else:
            sentences.append(f"यह दवा {medicine.medicine_name} है।")
        if match_type != EXACT:
            sentences.append("यह केवल एक संभावित मिलान है। कृपया packet पर छपा "
                             "नाम ज़रूर जाँचें।")
        if uses:
            shown = [use.lower() for use in uses[:3]]
            joined = ", ".join(shown[:-1]) + ((" और " + shown[-1]) if len(shown) > 1 else "")
            sentences.append(f"इसका उपयोग आमतौर पर {joined} के लिए किया जाता है।")
        if medicine.administration:
            sentences.append("इसे लेने का सामान्य तरीका: "
                             + medicine.administration.rstrip(".") + "।")
        if medicine.serious_warnings:
            first = medicine.serious_warnings.split(". ")[0].rstrip(".")
            sentences.append("महत्वपूर्ण चेतावनी: " + first + "।")
        if packaging is not None and packaging.expiry_raw:
            status = packaging.expiry_status()
            if status == EXPIRED:
                sentences.append("फोटो से पढ़ी तारीख के अनुसार यह packet समाप्त "
                                 "हो चुका है। इसका उपयोग न करें।")
            elif status == EXPIRING_SOON:
                sentences.append("फोटो के अनुसार यह packet जल्द समाप्त होने वाला "
                                 "है। उपयोग से पहले फार्मासिस्ट से पूछें।")
            else:
                sentences.append("फोटो के अनुसार यह packet समाप्त नहीं हुआ है। "
                                 "फिर भी packet पर तारीख ज़रूर जाँचें।")
        elif packaging is not None:
            sentences.append("फोटो से समाप्ति तिथि नहीं पढ़ी जा सकी। कृपया packet "
                             "स्वयं जाँचें।")
        else:
            sentences.append("उपयोग से पहले packet पर छपी समाप्ति तिथि ज़रूर जाँचें।")
        sentences.append("यह केवल सामान्य जानकारी है, चिकित्सा सलाह नहीं। हमेशा अपने "
                         "डॉक्टर या फार्मासिस्ट के निर्देशों का पालन करें।")
        return " ".join(sentences)

    # ------------------------- English version -------------------------
    if strength and strength.split()[0] not in medicine.medicine_name:
        sentences.append(f"This medicine is {medicine.medicine_name}, strength {strength}.")
    else:
        sentences.append(f"This medicine is {medicine.medicine_name}.")
    if match_type != EXACT:
        sentences.append(
            "This is a possible match only. Please confirm the exact name "
            "printed on the packaging."
        )
    if uses:
        shown = [use.lower() for use in uses[:3]]
        joined = ", ".join(shown[:-1]) + ((" and " + shown[-1]) if len(shown) > 1 else "")
        sentences.append(f"It is commonly used for {joined}.")
    if medicine.administration:
        sentences.append("How it is generally taken: "
                         + medicine.administration.rstrip(".") + ".")
    if medicine.serious_warnings:
        first = medicine.serious_warnings.split(". ")[0].rstrip(".")
        sentences.append("Important warning: " + first + ".")
    if packaging is not None and packaging.expiry_raw:
        status = packaging.expiry_status()
        if status == EXPIRED:
            sentences.append("According to the date read from the photo, "
                             "this pack has expired. Do not use it.")
        elif status == EXPIRING_SOON:
            sentences.append("According to the photo, this pack is expiring "
                             "soon. Ask a pharmacist before use.")
        else:
            sentences.append("According to the photo, this pack is not "
                             "expired. Still, confirm the date on the pack.")
    elif packaging is not None:
        sentences.append("The expiry date could not be read from the photo. "
                         "Please check the pack yourself.")
    else:
        sentences.append("Please check the expiry date printed on the pack "
                         "before using it.")
    sentences.append(
        "This is general information only, not medical advice. "
        "Always follow your doctor or pharmacist's instructions."
    )
    return " ".join(sentences)


# ---------------------------------------------------------------------------
# Phase 9 (v0.5): SIMPLE explanation page - short, elder-friendly.
# IMPORTANT: safety lines are NEVER dropped at this level.
# ---------------------------------------------------------------------------
def _first_sentence(text: str) -> str:
    """First sentence of a text (kept whole when already short)."""
    text = (text or "").strip()
    if not text:
        return ""
    for cut in (". ", "। ", ".\n"):
        if cut in text:
            return text.split(cut, 1)[0].rstrip(".।") + "."
    return text


def _format_simple_page(
    medicine: Medicine,
    match_type: Optional[str] = EXACT,
    language: str = EN,
) -> str:
    """
    The SIMPLE details page: name, confidence, what it is (one line),
    top uses, how taken, FULL safety warnings, storage, short disclaimer.
    """
    out: List[str] = []
    add = out.append
    na = _na(language)

    add(LINE)
    add(f"  {medicine.medicine_name}")
    add(LINE)
    add(f"  {_confidence_line(match_type, language)}")
    add(f"  {t('generic_lbl', language)} : {medicine.generic_name or na}")
    add(f"  {t('strength_lbl', language)} : {medicine.strength or na}")
    if medicine.is_demo_data():
        add(f"  {t('demo_source', language)}")

    add("")
    add(f">> {t('what_is', language)}")
    add(THIN_LINE)
    if medicine.general_usage:
        add(f"  {_first_sentence(medicine.general_usage)}")
    elif medicine.category:
        add(f"  {t('official_category', language)}: {medicine.category}")
    else:
        add(f"  {na}")
    if medicine.category:
        simple = explain_in_simple_words(medicine.category, language)
        if simple:
            add(f"  {simple}")

    add("")
    add(f">> {t('uses_hdr', language)}")
    add(THIN_LINE)
    uses = medicine.uses_list()
    if uses:
        for use in uses[:4]:
            add(f"  - {use}")
    else:
        add(f"  {na}")

    add("")
    add(f">> {t('how_taken', language)}")
    add(THIN_LINE)
    add(f"  {_first_sentence(medicine.administration) if medicine.administration else na}")

    # ---- SAFETY: always complete, never simplified away ----
    add("")
    add(f">> {t('safety_hdr', language)}")
    add(THIN_LINE)
    any_warning = False
    for field_name, label_key in WARNING_FIELDS:
        value = getattr(medicine, field_name, None)
        if value:
            add(f"  * {t(label_key, language)}: {value}")
            any_warning = True
    if not any_warning:
        add(f"  {na}")
    add("")
    add(f"  {t('serious_signs', language)}")
    add(f"     {medicine.serious_warnings or na}")

    if medicine.storage_information:
        add("")
        add(f">> {t('storage_card', language)}")
        add(THIN_LINE)
        add(f"  {medicine.storage_information}")

    disclaimer = DISCLAIMER_HI if language == HI else DISCLAIMER
    add("")
    add(LINE)
    add(f"  {t('disclaimer_lbl', language)}: {disclaimer}")
    add(LINE)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Phase 9 (v0.5): "Medicine feasibility" cards - who can take it + storage.
# Honest rule: only what the database VERIFIED is shown; nothing is guessed.
# ---------------------------------------------------------------------------
def format_age_suitability(medicine: Medicine, language: str = EN) -> str:
    """
    Child / elderly / pregnancy rows for a medicine, taken only from the
    verified warning fields. Missing data becomes the honest
    "Not available" line - the app never says "safe" on its own.
    """
    na = _na(language)
    rows: List[str] = []
    if language == HI:
        fields = [
            ("बच्चे",          medicine.children_warning),
            ("बुजुर्ग (65+)",  medicine.elderly_warning),
            ("गर्भवती महिलाएँ", medicine.pregnancy_warning),
            ("स्तनपान कराती माताएँ", medicine.breastfeeding_warning),
        ]
        note = ("ध्यान दें: यहाँ \"ठीक है\" जैसा कुछ लिखा होने पर भी, सही dose और "
                "फैसला डॉक्टर/फार्मासिस्ट ही बताते हैं।")
    else:
        fields = [
            ("Children",            medicine.children_warning),
            ("Elderly (65+)",       medicine.elderly_warning),
            ("Pregnant women",      medicine.pregnancy_warning),
            ("Breastfeeding women", medicine.breastfeeding_warning),
        ]
        note = ("Note: only the doctor/pharmacist can decide the right dose "
                "and whether it suits a particular person.")
    for label, value in fields:
        rows.append(f"  {label:<22}: {value or na}")
    rows.append("")
    rows.append(f"  {note}")
    return "\n".join(rows)


def format_storage_card(medicine: Medicine, language: str = EN) -> str:
    """
    Storage guidance for ONE medicine: the verified storage_information
    from the database, plus one gentle general reminder. Never guessed.
    """
    na = _na(language)
    if language == HI:
        head = "packet के label / डेटाबेस के अनुसार"
        tip = ("सामान्य नियम: अधिकतर दवाएँ ठंडी, सूखी जगह, धूप से दूर और बच्चों "
               "की पहुँच से बाहर रखें। Label पर अलग लिखा हो तो वही मानें।")
    else:
        head = "as per the package label / database"
        tip = ("General rule: keep most medicines in a cool, dry place away "
               "from sunlight, out of children's reach. If the label says "
               "something different, the label wins.")
    return f"  {head}:\n  {medicine.storage_information or na}\n\n  {tip}"


# ---------------------------------------------------------------------------
# Phase 9 (v0.5): Authenticity CHECKLIST.
# The app can NOT judge from a photo whether a medicine is real or fake -
# so instead of a fake verdict it gives an honest, practical checklist.
# ---------------------------------------------------------------------------
def format_authenticity_checklist(language: str = EN) -> str:
    """Honest genuineness checklist (no fake 'real/fake' verdict)."""
    if language == HI:
        intro = ("कोई भी ऐप सिर्फ फोटो से यह पक्का नहीं बता सकता कि दवा असली है या "
                 "नकली - इसलिए हम अनुमान नहीं लगाते। packet पर ये बातें ज़रूर जाँचें:")
        points = [
            "1. नाम बिल्कुल वही हो - असली packet पर brand और generic सही spelling के साथ छपे होते हैं।",
            "2. Batch नंबर, MFG तारीख और EXP (समाप्ति) तारीख साफ छपी हो - मिटी/कटी हुई न हो।",
            "3. MRP (कीमत) छपी हो और strip/bottle कहीं से फटी या दोबारा चिपकाई हुई न लगे।",
            "4. निर्माता कंपनी (Manufacturer) का नाम और पता छपा हो।",
            "5. दवा हमेशा दर्ज chemist/medical store से लें और बिल (रसीद) ज़रूर रखें।",
            "6. कोई भी शक हो तो packet अपने फार्मासिस्ट को दिखाएँ - वही सबसे अच्छी जाँच है।",
        ]
        tail = ("अगर इनमें से कुछ भी गलत या अधूरा लगे, तो दवा लेने से पहले "
                "फार्मासिस्ट/डॉक्टर से पूछें।")
    else:
        intro = ("No app can prove from a photo alone whether a medicine is real "
                 "or fake - so we never guess. Please check these on the pack:")
        points = [
            "1. Exact name - genuine packs print the brand and generic with correct spelling.",
            "2. Batch number, MFG date and EXP (expiry) date are clearly printed - not smudged or cut.",
            "3. MRP (price) is printed, and the strip/bottle is not torn or re-sealed.",
            "4. The manufacturer company's name and address are printed.",
            "5. Always buy from a registered chemist/medical store and keep the bill (receipt).",
            "6. When in any doubt, show the pack to your pharmacist - that is the best check.",
        ]
        tail = ("If anything looks wrong or is missing, ask a pharmacist/doctor "
                "before taking the medicine.")
    return intro + "\n\n" + "\n\n".join(points) + "\n\n" + tail


# ---------------------------------------------------------------------------
# Phase 9 (v0.5): spoken lines for reminders and the cabinet
# ---------------------------------------------------------------------------
def build_reminder_spoken(member: str, medicine_name: str,
                          strength=None, language: str = EN) -> str:
    """
    What the app SAYS when a dose becomes due, e.g.
    'Dadi, it is time for your medicine: Paracetamol 500, 500 milligrams.'
    """
    strength_say = _speakable_strength(strength, language) if strength else ""
    name = medicine_name or ("दवा" if language == HI else "your medicine")
    who = member or ("आप" if language == HI else "you")
    if language == HI:
        if strength_say:
            return (f"{who}, दवा लेने का समय हो गया है: {name}, {strength_say}। "
                    f"कृपया अपनी dose ले लीजिए।")
        return (f"{who}, दवा लेने का समय हो गया है: {name}। "
                f"कृपया अपनी dose ले लीजिए।")
    if strength_say:
        return (f"{who}, it is time for your medicine: {name}, {strength_say}. "
                f"Please take your dose.")
    return (f"{who}, it is time for your medicine: {name}. "
            f"Please take your dose.")


def build_cabinet_spoken_summary(summary: dict, language: str = EN) -> str:
    """
    Spoken version of the expiry dashboard:
    'Your cabinet has 5 medicines. 3 are within date, 1 is expiring soon,
     and 1 has expired - please do not use it.'
    `summary` is the dict from database.cabinet_expiry_summary().
    """
    valid = len(summary.get("valid", []))
    soon = len(summary.get("soon", []))
    expired = len(summary.get("expired", []))
    nodate = len(summary.get("nodate", []))
    total = valid + soon + expired + nodate
    if language == HI:
        if total == 0:
            return ("आपकी medicine cabinet खाली है। दवाएँ जोड़ने के लिए "
                    "'Add medicine' दबाएँ।")
        parts = [f"आपकी cabinet में कुल {total} दवाएँ हैं।"]
        if valid:
            parts.append(f"{valid} दवाएँ तारीख के भीतर हैं।")
        if soon:
            parts.append(f"{soon} दवाएँ जल्द समाप्त होने वाली हैं - कृपया "
                         f"फार्मासिस्ट से पूछकर उपयोग करें।")
        if expired:
            parts.append(f"{expired} दवाएँ समाप्त हो चुकी हैं - कृपया इनका "
                         f"उपयोग बिल्कुल न करें।")
        if nodate:
            parts.append(f"{nodate} दवाओं की तारीख दर्ज नहीं है - packet पर "
                         f"छपी expiry ज़रूर जाँचें।")
        return " ".join(parts)
    if total == 0:
        return ("Your medicine cabinet is empty. Tap 'Add medicine' to start "
                "adding the medicines you keep at home.")
    parts = [f"Your cabinet has {total} medicine{'s' if total != 1 else ''}."]
    if valid:
        parts.append(f"{valid} {'are' if valid != 1 else 'is'} within date.")
    if soon:
        parts.append(f"{soon} {'are' if soon != 1 else 'is'} expiring soon - "
                     f"please confirm with a pharmacist before use.")
    if expired:
        parts.append(f"{expired} {'have' if expired != 1 else 'has'} expired - "
                     f"please do NOT use {'them' if expired != 1 else 'it'}.")
    if nodate:
        parts.append(f"{nodate} {'have' if nodate != 1 else 'has'} no date "
                     f"recorded - please check the printed expiry on the pack.")
    return " ".join(parts)
