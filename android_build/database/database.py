"""
database.py
-----------
Everything about the local SQLite database lives here:

  * get_connection()        -> open a connection to the .db file
  * initialize_database()   -> create ALL tables (safe to re-run)
  * insert_medicine()       -> add one medicine row
  * fetch_all_medicines()   -> read every row as Medicine objects
  * Phase 8: history        -> text-only record of opened medicines
  * Phase 9: settings, family members, medicine cabinet,
             reminders and dose logs (all local + offline)

Privacy note: SQLite is a single local file on the user's own phone.
Nothing is sent anywhere - there is no server and no internet involved.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional

from .models import (Medicine, HistoryEntry, FamilyMember, CabinetItem,
                     Reminder, DoseLog)

# The database file lives inside the `database/` folder, next to this file.
DB_PATH = Path(__file__).resolve().parent / "medicine_database.db"

# ---------------------------------------------------------------------------
# Table schema — mirrors the fields requested in the project specification.
# ---------------------------------------------------------------------------
CREATE_MEDICINES_TABLE = """
CREATE TABLE IF NOT EXISTS medicines (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name         TEXT NOT NULL,
    brand_name            TEXT,
    generic_name          TEXT,
    active_ingredient     TEXT,
    strength              TEXT,
    category              TEXT,
    common_uses           TEXT,
    general_usage         TEXT,
    administration        TEXT,
    common_side_effects   TEXT,
    serious_warnings      TEXT,
    pregnancy_warning     TEXT,
    breastfeeding_warning TEXT,
    children_warning      TEXT,
    elderly_warning       TEXT,
    kidney_warning        TEXT,
    liver_warning         TEXT,
    drug_interactions     TEXT,
    food_interactions     TEXT,
    storage_information   TEXT,
    manufacturer          TEXT,
    dosage_form           TEXT,
    source                TEXT,
    last_updated          TEXT
);
"""

# Index speeds up name lookups once the database grows.
CREATE_NAME_INDEX = """
CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines (medicine_name);
"""

# Phase 8: local history of opened medicines (text only - never photos).
CREATE_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id   INTEGER,
    medicine_name TEXT NOT NULL,
    match_type    TEXT,
    searched_at   TEXT NOT NULL,
    expiry_status TEXT,
    source        TEXT DEFAULT 'search'
);
"""

# Phase 9: tiny key/value store for user settings (language, dark mode...).
CREATE_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""

# Phase 9: family members whose medicines the user manages (incl. self).
CREATE_FAMILY_TABLE = """
CREATE TABLE IF NOT EXISTS family_members (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    relation   TEXT,
    created_at TEXT
);
"""

# Phase 9: the Medicine Cabinet - real packs the user owns.
CREATE_CABINET_TABLE = """
CREATE TABLE IF NOT EXISTS cabinet (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name TEXT NOT NULL,
    strength      TEXT,
    quantity      REAL,
    quantity_unit TEXT DEFAULT 'tablets',
    dosage        TEXT,
    expiry_date   TEXT,
    storage_place TEXT,
    member_id     INTEGER,
    created_at    TEXT
);
"""

# Phase 9: daily dose reminders (times stored as "08:00,20:30").
CREATE_REMINDERS_TABLE = """
CREATE TABLE IF NOT EXISTS reminders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id     INTEGER,
    member_name   TEXT NOT NULL,
    medicine_name TEXT NOT NULL,
    strength      TEXT,
    times_csv     TEXT NOT NULL DEFAULT '08:00',
    active        INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT
);
"""

# Phase 9: what happened to each scheduled dose (taken / snoozed).
CREATE_DOSELOGS_TABLE = """
CREATE TABLE IF NOT EXISTS dose_logs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    reminder_id  INTEGER NOT NULL,
    log_date     TEXT NOT NULL,
    log_time     TEXT NOT NULL,
    status       TEXT NOT NULL,
    taken_at     TEXT,
    snooze_until TEXT
);
"""

# Ordered list of insertable columns (everything except the auto `id`).
MEDICINE_COLUMNS = [
    "medicine_name", "brand_name", "generic_name", "active_ingredient",
    "strength", "category", "common_uses", "general_usage", "administration",
    "common_side_effects", "serious_warnings", "pregnancy_warning",
    "breastfeeding_warning", "children_warning", "elderly_warning",
    "kidney_warning", "liver_warning", "drug_interactions",
    "food_interactions", "storage_information", "manufacturer",
    "dosage_form", "source", "last_updated",
]


def _now() -> str:
    """'YYYY-MM-DD HH:MM' local time stamp used across the app."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def get_connection(db_path=None) -> sqlite3.Connection:
    """
    Open (and create if needed) the SQLite database file.

    `row_factory = sqlite3.Row` lets us access columns by name, which
    `Medicine.from_row()` relies on.
    """
    path = Path(db_path) if db_path else DB_PATH
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    """Create the tables and index if they do not exist yet. Safe to re-run."""
    cursor = connection.cursor()
    cursor.execute(CREATE_MEDICINES_TABLE)
    cursor.execute(CREATE_NAME_INDEX)
    cursor.execute(CREATE_HISTORY_TABLE)
    cursor.execute(CREATE_SETTINGS_TABLE)
    cursor.execute(CREATE_FAMILY_TABLE)
    cursor.execute(CREATE_CABINET_TABLE)
    cursor.execute(CREATE_REMINDERS_TABLE)
    cursor.execute(CREATE_DOSELOGS_TABLE)
    connection.commit()


def insert_medicine(connection: sqlite3.Connection, data: dict) -> int:
    """
    Insert one medicine described by `data` (a dict of column -> value).

    Uses parameter placeholders (?) so values are never glued into SQL —
    this prevents SQL injection even if data comes from an untrusted file.
    Returns the new row's id.
    """
    # Keep only columns the table actually has; missing ones become None.
    safe_data = {column: data.get(column) for column in MEDICINE_COLUMNS}
    placeholders = ", ".join("?" for _ in MEDICINE_COLUMNS)
    sql = (
        f"INSERT INTO medicines ({', '.join(MEDICINE_COLUMNS)}) "
        f"VALUES ({placeholders})"
    )
    cursor = connection.cursor()
    cursor.execute(sql, [safe_data[column] for column in MEDICINE_COLUMNS])
    connection.commit()
    return cursor.lastrowid


def fetch_all_medicines(connection: sqlite3.Connection) -> List[Medicine]:
    """Return every medicine in the database as Medicine objects (A–Z)."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM medicines ORDER BY medicine_name COLLATE NOCASE")
    return [Medicine.from_row(row) for row in cursor.fetchall()]


def count_medicines(connection: sqlite3.Connection) -> int:
    """Return how many medicine rows exist."""
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM medicines")
    return cursor.fetchone()[0]


def get_medicine_by_id(connection: sqlite3.Connection, medicine_id: int) -> Optional[Medicine]:
    """Fetch one medicine by its id (used by History). None if it no longer exists."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,))
    row = cursor.fetchone()
    return Medicine.from_row(row) if row else None


# --------------------------------------------------------------------------
# Phase 8: medicine history (local, private, text-only)
# --------------------------------------------------------------------------
def add_history_entry(
    connection: sqlite3.Connection,
    medicine: Medicine,
    match_type: Optional[str],
    expiry_status: Optional[str] = None,
    source: str = "search",
) -> int:
    """Record that the user opened a medicine's details. Returns the new id."""
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO history (medicine_id, medicine_name, match_type, searched_at,"
        " expiry_status, source) VALUES (?, ?, ?, ?, ?, ?)",
        (
            medicine.id,
            medicine.medicine_name,
            match_type,
            _now(),
            expiry_status,
            source,
        ),
    )
    connection.commit()
    return cursor.lastrowid


def fetch_history(connection: sqlite3.Connection) -> List[HistoryEntry]:
    """All history entries, newest first."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM history ORDER BY id DESC")
    return [HistoryEntry.from_row(row) for row in cursor.fetchall()]


def delete_history_entry(connection: sqlite3.Connection, entry_id: int) -> bool:
    """Delete ONE history entry by id. Returns True if something was deleted."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM history WHERE id = ?", (entry_id,))
    connection.commit()
    return cursor.rowcount > 0


def clear_history(connection: sqlite3.Connection) -> int:
    """Delete ALL history entries. Returns how many were deleted."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM history")
    connection.commit()
    return cursor.rowcount


# --------------------------------------------------------------------------
# Phase 9: settings (tiny key/value store)
# --------------------------------------------------------------------------
def get_setting(connection: sqlite3.Connection, key: str,
                default: Optional[str] = None) -> Optional[str]:
    """Read one setting; returns `default` when the key was never saved."""
    cursor = connection.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    return row["value"] if row else default


def set_setting(connection: sqlite3.Connection, key: str, value: str) -> None:
    """Save one setting (insert or overwrite)."""
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )
    connection.commit()


# --------------------------------------------------------------------------
# Phase 9: family members
# --------------------------------------------------------------------------
def add_family_member(connection: sqlite3.Connection, name: str,
                      relation: Optional[str] = None) -> int:
    """Add a person (e.g. 'Dadi', relation 'Grandmother'). Returns the new id."""
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO family_members (name, relation, created_at)"
        " VALUES (?, ?, ?)",
        (name.strip(), (relation or "").strip() or None, _now()),
    )
    connection.commit()
    return cursor.lastrowid


def fetch_family_members(connection: sqlite3.Connection) -> List[FamilyMember]:
    """All family members, oldest first (self is usually added first)."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM family_members ORDER BY id")
    return [FamilyMember.from_row(row) for row in cursor.fetchall()]


def delete_family_member(connection: sqlite3.Connection, member_id: int) -> None:
    """
    Remove a member. Their reminders (and the dose logs of those reminders)
    go away too; cabinet items are kept but become 'shared' (member_id NULL).
    """
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM reminders WHERE member_id = ?", (member_id,))
    reminder_ids = [row["id"] for row in cursor.fetchall()]
    for rid in reminder_ids:
        cursor.execute("DELETE FROM dose_logs WHERE reminder_id = ?", (rid,))
    cursor.execute("DELETE FROM reminders WHERE member_id = ?", (member_id,))
    cursor.execute("UPDATE cabinet SET member_id = NULL WHERE member_id = ?",
                   (member_id,))
    cursor.execute("DELETE FROM family_members WHERE id = ?", (member_id,))
    connection.commit()


# --------------------------------------------------------------------------
# Phase 9: medicine cabinet
# --------------------------------------------------------------------------
def _normalise_expiry(raw: Optional[str]) -> Optional[str]:
    """
    Best-effort normalisation of a typed expiry to "YYYY-MM" / "YYYY-MM-DD".
    Also accepts "MM/YYYY" and "MM-YYYY". Anything unreadable is returned
    unchanged (CabinetItem.effective_expiry treats it as 'no date') - the
    app NEVER invents or guesses a date.
    """
    if not raw:
        return None
    text = raw.strip().replace("/", "-").replace(".", "-")
    if not text:
        return None
    parts = [p for p in text.split("-") if p]
    try:
        if len(parts) == 2 and len(parts[0]) == 4:          # YYYY-MM
            year, month = int(parts[0]), int(parts[1])
            if 1 <= month <= 12:
                return f"{year:04d}-{month:02d}"
        if len(parts) == 2 and len(parts[1]) == 4:          # MM-YYYY
            month, year = int(parts[0]), int(parts[1])
            if 1 <= month <= 12:
                return f"{year:04d}-{month:02d}"
        if len(parts) == 3 and len(parts[0]) == 4:          # YYYY-MM-DD
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            if 1 <= month <= 12 and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}"
    except ValueError:
        pass
    return text or None


def add_cabinet_item(connection: sqlite3.Connection, data: dict) -> int:
    """
    Add one cabinet item (dict with keys: medicine_name, strength, quantity,
    quantity_unit, dosage, expiry_date, storage_place, member_id).
    Returns the new row id.
    """
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO cabinet (medicine_name, strength, quantity, quantity_unit,"
        " dosage, expiry_date, storage_place, member_id, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            (data.get("medicine_name") or "").strip(),
            (data.get("strength") or "").strip() or None,
            data.get("quantity"),
            (data.get("quantity_unit") or "").strip() or "tablets",
            (data.get("dosage") or "").strip() or None,
            _normalise_expiry(data.get("expiry_date")),
            (data.get("storage_place") or "").strip() or None,
            data.get("member_id"),
            _now(),
        ),
    )
    connection.commit()
    return cursor.lastrowid


def fetch_cabinet(connection: sqlite3.Connection) -> List[CabinetItem]:
    """All cabinet items, oldest first."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cabinet ORDER BY id")
    return [CabinetItem.from_row(row) for row in cursor.fetchall()]


def update_cabinet_quantity(connection: sqlite3.Connection, item_id: int,
                            quantity: Optional[float]) -> None:
    """Set the remaining quantity of one cabinet item (e.g. after a dose)."""
    cursor = connection.cursor()
    cursor.execute("UPDATE cabinet SET quantity = ? WHERE id = ?",
                   (quantity, item_id))
    connection.commit()


def delete_cabinet_item(connection: sqlite3.Connection, item_id: int) -> None:
    """Remove one cabinet item."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM cabinet WHERE id = ?", (item_id,))
    connection.commit()


def cabinet_expiry_summary(connection: sqlite3.Connection, today=None) -> dict:
    """
    Split the cabinet into 4 honest buckets by printed expiry:
      {"valid": [...], "soon": [...], "expired": [...], "nodate": [...]}
    Used by the Expiry dashboard, the cabinet strip and the spoken summary.
    """
    buckets = {"valid": [], "soon": [], "expired": [], "nodate": []}
    for item in fetch_cabinet(connection):
        state = item.expiry_state(today)
        if state == "valid":
            buckets["valid"].append(item)
        elif state == "expiring_soon":
            buckets["soon"].append(item)
        elif state == "expired":
            buckets["expired"].append(item)
        else:
            buckets["nodate"].append(item)
    return buckets


# --------------------------------------------------------------------------
# Phase 9: reminders
# --------------------------------------------------------------------------
def _clean_times(times_text: Optional[str]) -> str:
    """
    Validate "HH:MM, HH:MM" 24h times, drop typos, sort them.
    If nothing valid remains, fall back to one morning slot "08:00".
    """
    from datetime import datetime
    valid = []
    for piece in (times_text or "").split(","):
        piece = piece.strip()
        try:
            datetime.strptime(piece, "%H:%M")
            valid.append(piece)
        except ValueError:
            continue
    if not valid:
        valid = ["08:00"]
    return ",".join(sorted(set(valid)))


def add_reminder(connection: sqlite3.Connection, member_id: Optional[int],
                 member_name: str, medicine_name: str,
                 strength: Optional[str], times_text: str) -> int:
    """Add a daily reminder. Returns the new id."""
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO reminders (member_id, member_name, medicine_name,"
        " strength, times_csv, active, created_at) VALUES (?, ?, ?, ?, ?, 1, ?)",
        (member_id, (member_name or "").strip() or "Self",
         (medicine_name or "").strip(),
         (strength or "").strip() or None,
         _clean_times(times_text), _now()),
    )
    connection.commit()
    return cursor.lastrowid


def fetch_reminders(connection: sqlite3.Connection,
                    active_only: bool = False) -> List[Reminder]:
    """All reminders (or only the switched-on ones), oldest first."""
    cursor = connection.cursor()
    if active_only:
        cursor.execute("SELECT * FROM reminders WHERE active = 1 ORDER BY id")
    else:
        cursor.execute("SELECT * FROM reminders ORDER BY id")
    return [Reminder.from_row(row) for row in cursor.fetchall()]


def set_reminder_active(connection: sqlite3.Connection, reminder_id: int,
                        active: bool) -> None:
    """Switch one reminder on/off."""
    cursor = connection.cursor()
    cursor.execute("UPDATE reminders SET active = ? WHERE id = ?",
                   (1 if active else 0, reminder_id))
    connection.commit()


def delete_reminder(connection: sqlite3.Connection, reminder_id: int) -> None:
    """Delete a reminder and all its dose logs."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM dose_logs WHERE reminder_id = ?", (reminder_id,))
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    connection.commit()


# --------------------------------------------------------------------------
# Phase 9: dose logs (taken / snoozed)
# --------------------------------------------------------------------------
def upsert_dose_log(connection: sqlite3.Connection, reminder_id: int,
                    log_date: str, log_time: str, status: str,
                    taken_at: Optional[str] = None,
                    snooze_until: Optional[str] = None) -> int:
    """
    Record the outcome of one scheduled dose ("YYYY-MM-DD" + "HH:MM").
    Pressing a button twice for the SAME slot replaces the old record
    instead of piling up duplicates.
    """
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM dose_logs WHERE reminder_id = ? AND log_date = ?"
        " AND log_time = ?",
        (reminder_id, log_date, log_time),
    )
    cursor.execute(
        "INSERT INTO dose_logs (reminder_id, log_date, log_time, status,"
        " taken_at, snooze_until) VALUES (?, ?, ?, ?, ?, ?)",
        (reminder_id, log_date, log_time, status, taken_at, snooze_until),
    )
    connection.commit()
    return cursor.lastrowid


def get_dose_log(connection: sqlite3.Connection, reminder_id: int,
                 log_date: str, log_time: str) -> Optional[DoseLog]:
    """The recorded outcome of one scheduled dose slot, or None."""
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM dose_logs WHERE reminder_id = ? AND log_date = ?"
        " AND log_time = ?",
        (reminder_id, log_date, log_time),
    )
    row = cursor.fetchone()
    return DoseLog.from_row(row) if row else None


def fetch_dose_logs(connection: sqlite3.Connection,
                    log_date: Optional[str] = None) -> List[DoseLog]:
    """All dose logs, newest first (optionally only for one date)."""
    cursor = connection.cursor()
    if log_date:
        cursor.execute("SELECT * FROM dose_logs WHERE log_date = ?"
                       " ORDER BY id DESC", (log_date,))
    else:
        cursor.execute("SELECT * FROM dose_logs ORDER BY id DESC")
    return [DoseLog.from_row(row) for row in cursor.fetchall()]


def clear_dose_logs(connection: sqlite3.Connection) -> int:
    """Delete ALL dose logs (used by 'Clear history & logs')."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM dose_logs")
    connection.commit()
    return cursor.rowcount


def count_today_doses(connection: sqlite3.Connection, today: str):
    """
    (taken, scheduled) dose count for one date ("YYYY-MM-DD").
    scheduled = total slots of all ACTIVE reminders for the day;
    taken     = dose logs with status 'taken' for the date.
    The home status pill shows exactly this: "2 of 3 doses taken today".
    """
    scheduled = 0
    for reminder in fetch_reminders(connection, active_only=True):
        scheduled += len(reminder.times())
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM dose_logs WHERE log_date = ?"
                   " AND status = 'taken'", (today,))
    taken = cursor.fetchone()[0]
    return taken, scheduled
