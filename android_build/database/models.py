"""
models.py
---------
Defines the dataclasses the app works with instead of raw database rows.

  * Medicine      -> one row of the `medicines` table (reference knowledge)
  * HistoryEntry  -> one row of local search/scan history
  * FamilyMember  -> a person whose medicines the user manages (self, dadi...)
  * CabinetItem   -> a physical medicine the user owns (quantity, dosage, expiry)
  * Reminder      -> a scheduled dose time for a member + medicine
  * DoseLog       -> record of a taken / snoozed scheduled dose

Everything is plain Python, beginner-friendly, and 100% local/offline.
"""

from dataclasses import dataclass, fields
from typing import List, Optional


def split_field(value: Optional[str]) -> List[str]:
    """
    Convert a ';'-separated database text field into a clean Python list.

    Example: "Fever; Headache; Body pain" -> ["Fever", "Headache", "Body pain"]
    Empty/None values become an empty list — the app never invents content.
    """
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def _from_row(cls, row):
    """Shared sqlite3.Row -> dataclass builder (ignores unexpected columns)."""
    column_names = {f.name for f in fields(cls)}
    data = {key: value for key, value in dict(row).items() if key in column_names}
    return cls(**data)


@dataclass
class Medicine:
    # Only `id` and `medicine_name` are mandatory. Everything else is
    # Optional: if the database has no verified value, it stays None and
    # the UI will show "not available" instead of guessing.
    id: int
    medicine_name: str
    brand_name: Optional[str] = None
    generic_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    strength: Optional[str] = None
    category: Optional[str] = None
    common_uses: Optional[str] = None
    general_usage: Optional[str] = None
    administration: Optional[str] = None
    common_side_effects: Optional[str] = None
    serious_warnings: Optional[str] = None
    pregnancy_warning: Optional[str] = None
    breastfeeding_warning: Optional[str] = None
    children_warning: Optional[str] = None
    elderly_warning: Optional[str] = None
    kidney_warning: Optional[str] = None
    liver_warning: Optional[str] = None
    drug_interactions: Optional[str] = None
    food_interactions: Optional[str] = None
    storage_information: Optional[str] = None
    manufacturer: Optional[str] = None
    dosage_form: Optional[str] = None
    source: Optional[str] = None
    last_updated: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Medicine":
        return _from_row(cls, row)

    # --- Convenience helpers: list versions of ';'-separated fields ---
    def uses_list(self) -> List[str]:
        return split_field(self.common_uses)

    def side_effects_list(self) -> List[str]:
        return split_field(self.common_side_effects)

    def is_demo_data(self) -> bool:
        """True while the row is labelled demo/unverified data."""
        return bool(self.source) and "DEMO" in self.source.upper()


@dataclass
class HistoryEntry:
    """
    One row of the local search/scan history.

    Stores only lightweight TEXT information (medicine name, when,
    how it matched, expiry status if a photo was scanned).
    Photos are NEVER stored - the app keeps no medicine images at all.
    """
    id: int
    medicine_id: Optional[int]
    medicine_name: str
    match_type: Optional[str] = None       # 'exact' / 'possible'
    searched_at: Optional[str] = None      # "YYYY-MM-DD HH:MM" local time
    expiry_status: Optional[str] = None    # valid/expiring_soon/expired/None
    source: Optional[str] = None           # 'search' or 'scan'

    @classmethod
    def from_row(cls, row) -> "HistoryEntry":
        return _from_row(cls, row)


# ---------------------------------------------------------------------------
# Phase 9: your medicines, your people, your routine (all local + offline)
# ---------------------------------------------------------------------------
@dataclass
class FamilyMember:
    """Someone whose medicines you look after (including yourself)."""
    id: int
    name: str
    relation: Optional[str] = None       # e.g. "Self", "Dadi", "Papa"
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "FamilyMember":
        return _from_row(cls, row)


@dataclass
class CabinetItem:
    """
    One real medicine pack/strip the user owns (the 'Medicine Cabinet').

    `expiry_date` is stored as the user typed it: "YYYY-MM" or "YYYY-MM-DD".
    Month-only values follow the standard convention: valid until the END
    of the printed month (same rule the OCR/photo reader uses).
    """
    id: int
    medicine_name: str
    strength: Optional[str] = None
    quantity: Optional[float] = None     # e.g. 8  (tablets left)
    quantity_unit: Optional[str] = "tablets"
    dosage: Optional[str] = None         # e.g. "1 tablet twice a day"
    expiry_date: Optional[str] = None    # "YYYY-MM" or "YYYY-MM-DD"
    storage_place: Optional[str] = None  # e.g. "Bedroom drawer, away from sunlight"
    member_id: Optional[int] = None      # whose medicine (None = general/shared)
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "CabinetItem":
        return _from_row(cls, row)

    def effective_expiry(self):
        """
        Parse the typed expiry into a date.
        "YYYY-MM" -> last day of that month (printed-month convention).
        Returns a datetime.date or None when unreadable/missing.
        """
        from datetime import date as _date
        from utils.date_utils import _last_day
        raw = (self.expiry_date or "").strip()
        if not raw:
            return None
        parts = raw.replace("/", "-").split("-")
        try:
            if len(parts) == 2:                 # YYYY-MM
                year, month = int(parts[0]), int(parts[1])
                return _last_day(year, month)
            if len(parts) == 3:                 # YYYY-MM-DD
                return _date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return None
        return None

    def expiry_state(self, today=None) -> Optional[str]:
        """'valid' / 'expiring_soon' / 'expired', or None if no date typed."""
        from datetime import date as _date
        from datetime import timedelta
        from utils.date_utils import VALID, EXPIRING_SOON, EXPIRED, EXPIRING_SOON_DAYS
        eff = self.effective_expiry()
        if not eff:
            return None
        today = today or _date.today()
        if eff < today:
            return EXPIRED
        if eff <= today + timedelta(days=EXPIRING_SOON_DAYS):
            return EXPIRING_SOON
        return VALID


@dataclass
class Reminder:
    """
    A scheduled dose: WHO takes WHAT at WHICH time(s) of the day (daily).

    `times_csv` holds comma-separated "HH:MM" 24h times: "08:00,20:30".
    100% local - reminders are checked by the app while it is open,
    and the app then SPEAKS the reminder (voice assistant style).
    """
    id: int
    member_id: Optional[int]
    member_name: str                      # kept as text so deleting a member
    medicine_name: str                    # never breaks an existing reminder
    strength: Optional[str] = None
    times_csv: str = "08:00"
    active: int = 1                       # 1 = on, 0 = paused
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Reminder":
        return _from_row(cls, row)

    def times(self) -> List[str]:
        return [t.strip() for t in (self.times_csv or "").split(",") if t.strip()]


@dataclass
class DoseLog:
    """
    One scheduled dose outcome for one day:
      status 'taken'   -> user pressed Take Now (taken_at set)
      status 'snoozed' -> user pressed Snooze (snooze_until set; it becomes
                          due again after that moment unless taken)
    """
    id: int
    reminder_id: int
    log_date: str                         # "YYYY-MM-DD"
    log_time: str                         # scheduled "HH:MM"
    status: str                           # 'taken' / 'snoozed'
    taken_at: Optional[str] = None        # "YYYY-MM-DD HH:MM"
    snooze_until: Optional[str] = None    # "YYYY-MM-DD HH:MM"

    @classmethod
    def from_row(cls, row) -> "DoseLog":
        return _from_row(cls, row)
