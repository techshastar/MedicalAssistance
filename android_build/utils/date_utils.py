"""
date_utils.py  (Phase 5 - MFG / EXP / Batch reading & expiry status)
----------------------------------------------------------------------
Reads packaging information from OCR text:
    * Expiry date        (EXP, EXPIRY, USE BEFORE, ...)
    * Manufacturing date (MFG, MFD, MANUFACTURED...)
    * Batch number       (B.No, BATCH NO, LOT NO...)

If an expiry date IS found, it reports one of:
    VALID  (not expired)  /  EXPIRING SOON (within 30 days)  /  EXPIRED

⚠️ THE GOLDEN RULES (from the project spec) enforced here:
    1. We NEVER invent or estimate an exact expiry date. Dates are
       only accepted when they appear right next to a printed LABEL
       (exp/mfg/batch). Random numbers on a pack are never dates.
    2. If nothing readable is found -> the UI shows
       "Expiry date could not be detected. Please check the
        medicine packaging manually."  (NO_EXPIRY_MESSAGE)
    3. Month-only dates ("EXP 12/2027") use the standard convention
       "valid until the END of the printed month", and the display
       always says that this convention was used.
    4. We never claim a medicine is SAFE just because it is not
       expired - storage conditions matter. The UI says so too.
"""

import calendar
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Tuple

# ---- Expiry status values ------------------------------------------------
VALID = "valid"
EXPIRING_SOON = "expiring_soon"
EXPIRED = "expired"

# How close to expiry counts as "expiring soon".
EXPIRING_SOON_DAYS = 30

# The exact honest message required by the spec when nothing is readable.
NO_EXPIRY_MESSAGE = (
    "Expiry date could not be detected. "
    "Please check the medicine packaging manually."
)

# How far after a label we allow a date (labels and dates are close together).
_LABEL_WINDOW = 20

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Label patterns (case-insensitive).
LABEL_EXP = r"(?:exp(?:iry|iration|ired)?\.?|use\s*before|best\s*before)"
LABEL_MFG = r"(?:mfg\.?|mfd\.?|manufactur\w*)"
LABEL_BATCH = r"(?:b\.?\s*no\.?|batch(?:\s*(?:no|number)\.?)?|lot\s*(?:no|number)?\.?)"

# Date shapes that may appear inside the label window.
_MONTH_NAME = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
DATE_PATTERNS = [
    # Named month first - it is unambiguous: "Dec 2026", "Dec'26"
    ("named", re.compile(_MONTH_NAME + r"\s*'?\s*(\d{4})", re.I)),
    ("named_2y", re.compile(_MONTH_NAME + r"\s*'?\s*(\d{2})(?!\d)", re.I)),
    # Full numeric date: 12/12/2027 or 12 12 27 (day-first, Indian standard)
    ("full", re.compile(r"(\d{1,2})[ ./-](\d{1,2})[ ./-](\d{2,4})", re.I)),
    # Month/year: 12/2027
    ("month_year", re.compile(r"(\d{1,2})[ ./-](\d{4})", re.I)),
    # Month/short-year: 12/27
    ("month_2year", re.compile(r"(\d{1,2})[ ./-](\d{2})(?!\d)", re.I)),
]


@dataclass
class PackagingInfo:
    """Everything readable from a medicine pack's photo."""
    batch_number: Optional[str] = None
    mfg_raw: Optional[str] = None            # as printed, e.g. "01/2026"
    expiry_raw: Optional[str] = None         # as printed, e.g. "12/2027"
    expiry_date: Optional[date] = None       # effective date used for status
    expiry_month_only: bool = False          # True when pack shows only month
    mfg_date: Optional[date] = None
    mfg_month_only: bool = False

    def expiry_status(self, today: Optional[date] = None) -> Optional[str]:
        """VALID / EXPIRING_SOON / EXPIRED, or None if no expiry was read."""
        if not self.expiry_date:
            return None
        today = today or date.today()
        if self.expiry_date < today:
            return EXPIRED
        if self.expiry_date <= today + timedelta(days=EXPIRING_SOON_DAYS):
            return EXPIRING_SOON
        return VALID


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _year(two_or_four: str) -> int:
    """A 2-digit printed year means 20xx (standard pack convention)."""
    number = int(two_or_four)
    return 2000 + number if number < 100 else number


def _last_day(year: int, month: int) -> date:
    """For 'EXP 12/2027' packs: valid until the END of the printed month."""
    return date(year, month, calendar.monthrange(year, month)[1])


def _parse_date_in_window(window: str) -> Optional[Tuple[date, bool, str]]:
    """
    Try every known date shape inside the text window after a label.
    Returns (effective_date, month_only?, as_printed) or None.
    Never returns anything that is not actually printed there.
    """
    for kind, pattern in DATE_PATTERNS:
        match = pattern.search(window)
        if not match:
            continue
        try:
            if kind == "named":
                month = _MONTHS[match.group(1)[:3].lower()]
                return (_last_day(_year(match.group(2)), month), True, match.group(0))
            if kind == "named_2y":
                month = _MONTHS[match.group(1)[:3].lower()]
                return (_last_day(_year(match.group(2)), month), True, match.group(0))
            if kind == "full":
                a, b, c = int(match.group(1)), int(match.group(2)), _year(match.group(3))
                day, month = a, b
                try:
                    parsed = date(c, month, day)
                except ValueError:
                    # Maybe it was month-first; try the swap once.
                    parsed = date(c, day, month)
                return (parsed, False, match.group(0))
            if kind == "month_year":
                month = int(match.group(1))
                return (_last_day(_year(match.group(2)), month), True, match.group(0))
            if kind == "month_2year":
                month = int(match.group(1))
                return (_last_day(_year(match.group(2)), month), True, match.group(0))
        except (ValueError, KeyError):
            continue  # e.g. month 13 -> not a date, keep looking
    return None


def _find_labelled_date(text: str, label_pattern: str):
    """Find `label_pattern`, then look for a date right after the label."""
    for label in re.finditer(label_pattern, text, re.I):
        window = text[label.end(): label.end() + _LABEL_WINDOW]
        # The window must start with a separator (otherwise "EXPORT" etc.)
        if window and not window.startswith((" ", ":", ".", "-")):
            continue
        parsed = _parse_date_in_window(window)
        if parsed:
            return parsed
    return None


def _find_batch(text: str) -> Optional[str]:
    """Extract a batch/lot number printed after its label."""
    match = re.search(
        LABEL_BATCH + r"\s*[:.]?\s*([A-Za-z0-9][A-Za-z0-9\-]{2,14})", text, re.I
    )
    if not match:
        return None
    batch = match.group(1).strip()
    # A batch that is only a common word offers no identification value.
    if batch.lower() in {"no", "the", "and", "for", "not"}:
        return None
    return batch.upper()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def extract_packaging_info(text: str) -> PackagingInfo:
    """
    Read batch number, manufacturing date and expiry date from OCR text.

    Only LABELLED values are accepted. If a value is not readable it stays
    None - it is never guessed or estimated.
    """
    squashed = " ".join((text or "").split())

    info = PackagingInfo(batch_number=_find_batch(squashed))

    mfg = _find_labelled_date(squashed, LABEL_MFG)
    if mfg:
        info.mfg_date, info.mfg_month_only, info.mfg_raw = mfg

    expiry = _find_labelled_date(squashed, LABEL_EXP)
    if expiry:
        info.expiry_date, info.expiry_month_only, info.expiry_raw = expiry

    return info
