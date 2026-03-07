"""
SQLite database layer for the WhatsApp Chores Reminder app.
Handles chores, reminders, and conversation history.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = "chores.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS chores (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT,
                assigned_to TEXT DEFAULT 'both',
                due_date    TEXT,
                recurrence  TEXT,
                status      TEXT DEFAULT 'pending',
                created_by  TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                completed_at TEXT,
                completed_by TEXT
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                chore_id   INTEGER,
                remind_at  TEXT NOT NULL,
                message    TEXT NOT NULL,
                sent       INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (chore_id) REFERENCES chores(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS conversation_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                role         TEXT NOT NULL,
                content      TEXT NOT NULL,
                created_at   TEXT NOT NULL
            );
        """)


# ---------------------------------------------------------------------------
# Chore operations
# ---------------------------------------------------------------------------

def add_chore(
    title: str,
    created_by: str,
    description: Optional[str] = None,
    assigned_to: str = "both",
    due_date: Optional[str] = None,
    recurrence: Optional[str] = None,
) -> dict:
    if recurrence == "none":
        recurrence = None
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO chores
               (title, description, assigned_to, due_date, recurrence,
                created_by, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, description, assigned_to, due_date, recurrence, created_by, now),
        )
        chore_id = cursor.lastrowid
    return {
        "success": True,
        "chore_id": chore_id,
        "message": f"Added chore '{title}' as #{chore_id}",
    }


def list_chores(status: str = "pending", assigned_to: Optional[str] = None) -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    params: list = []
    query = "SELECT * FROM chores WHERE 1=1"

    if status == "pending":
        query += " AND status = 'pending'"
    elif status == "completed":
        query += " AND status = 'completed'"
    # 'all' → no filter

    if assigned_to:
        query += " AND (assigned_to = ? OR assigned_to = 'both')"
        params.append(assigned_to)

    query += " ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date ASC, created_at ASC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    chores = []
    for row in rows:
        chore = dict(row)
        chore["overdue"] = (
            bool(chore["due_date"])
            and chore["status"] == "pending"
            and chore["due_date"] < today
        )
        chores.append(chore)

    return {"chores": chores, "count": len(chores)}


def complete_chore(chore_id: int, completed_by: Optional[str] = None) -> dict:
    now = datetime.now().isoformat()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM chores WHERE id = ?", (chore_id,)).fetchone()
        if not row:
            return {"success": False, "error": f"Chore #{chore_id} not found"}

        chore = dict(row)
        conn.execute(
            "UPDATE chores SET status='completed', completed_at=?, completed_by=? WHERE id=?",
            (now, completed_by, chore_id),
        )

        next_id = None
        next_due = None
        if chore["recurrence"] and chore["recurrence"] != "none":
            next_due = _next_due_date(chore["due_date"], chore["recurrence"])
            cursor = conn.execute(
                """INSERT INTO chores
                   (title, description, assigned_to, due_date, recurrence,
                    created_by, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    chore["title"],
                    chore["description"],
                    chore["assigned_to"],
                    next_due,
                    chore["recurrence"],
                    chore["created_by"],
                    now,
                ),
            )
            next_id = cursor.lastrowid

    result: dict = {"success": True, "message": f"✅ Completed '{chore['title']}'!"}
    if next_id:
        result["next_occurrence_id"] = next_id
        result["message"] += f" Next due {next_due} (chore #{next_id} created)."
    return result


def delete_chore(chore_id: int) -> dict:
    with get_connection() as conn:
        row = conn.execute("SELECT title FROM chores WHERE id=?", (chore_id,)).fetchone()
        if not row:
            return {"success": False, "error": f"Chore #{chore_id} not found"}
        title = row["title"]
        conn.execute("DELETE FROM reminders WHERE chore_id=?", (chore_id,))
        conn.execute("DELETE FROM chores WHERE id=?", (chore_id,))
    return {"success": True, "message": f"Deleted '{title}' (#{chore_id})"}


def update_chore(chore_id: int, **kwargs) -> dict:
    allowed = {"title", "description", "assigned_to", "due_date", "recurrence", "status"}
    updates = {}
    for field in allowed:
        if field in kwargs and kwargs[field] is not None:
            val = kwargs[field]
            if field == "recurrence" and val == "none":
                val = None
            updates[field] = val

    if not updates:
        return {"success": False, "error": "No valid fields provided"}

    with get_connection() as conn:
        row = conn.execute("SELECT id FROM chores WHERE id=?", (chore_id,)).fetchone()
        if not row:
            return {"success": False, "error": f"Chore #{chore_id} not found"}

        set_clause = ", ".join(f"{k}=?" for k in updates)
        values = list(updates.values()) + [chore_id]
        conn.execute(f"UPDATE chores SET {set_clause} WHERE id=?", values)

    return {"success": True, "message": f"Updated chore #{chore_id}"}


def get_household_summary() -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    week_ahead = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    with get_connection() as conn:
        pending = conn.execute(
            "SELECT COUNT(*) FROM chores WHERE status='pending'"
        ).fetchone()[0]
        overdue = conn.execute(
            "SELECT COUNT(*) FROM chores WHERE status='pending' AND due_date < ?",
            (today,),
        ).fetchone()[0]
        due_week = conn.execute(
            "SELECT COUNT(*) FROM chores WHERE status='pending' AND due_date BETWEEN ? AND ?",
            (today, week_ahead),
        ).fetchone()[0]
        completed_today = conn.execute(
            "SELECT COUNT(*) FROM chores WHERE status='completed' AND completed_at >= ?",
            (today,),
        ).fetchone()[0]
        upcoming_reminders = conn.execute(
            "SELECT COUNT(*) FROM reminders WHERE sent=0"
        ).fetchone()[0]

    return {
        "total_pending": pending,
        "overdue": overdue,
        "due_this_week": due_week,
        "completed_today": completed_today,
        "upcoming_reminders": upcoming_reminders,
    }


# ---------------------------------------------------------------------------
# Reminder operations
# ---------------------------------------------------------------------------

def schedule_reminder(
    remind_at: str, message: str, chore_id: Optional[int] = None
) -> dict:
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO reminders (chore_id, remind_at, message, created_at) VALUES (?,?,?,?)",
            (chore_id, remind_at, message, now),
        )
        reminder_id = cursor.lastrowid
    return {
        "success": True,
        "reminder_id": reminder_id,
        "message": f"Reminder #{reminder_id} set for {remind_at}",
    }


def list_reminders() -> dict:
    now = datetime.now().isoformat()
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT r.*, c.title AS chore_title
               FROM reminders r
               LEFT JOIN chores c ON r.chore_id = c.id
               WHERE r.sent = 0 AND r.remind_at > ?
               ORDER BY r.remind_at ASC""",
            (now,),
        ).fetchall()
    reminders = [dict(r) for r in rows]
    return {"reminders": reminders, "count": len(reminders)}


def delete_reminder(reminder_id: int) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM reminders WHERE id=?", (reminder_id,)
        ).fetchone()
        if not row:
            return {"success": False, "error": f"Reminder #{reminder_id} not found"}
        conn.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
    return {"success": True, "message": f"Deleted reminder #{reminder_id}"}


def get_pending_reminders() -> list:
    """Return reminders whose time has arrived and haven't been sent yet."""
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM reminders WHERE sent=0 AND remind_at <= ?", (now,)
        ).fetchall()
    return [dict(r) for r in rows]


def mark_reminder_sent(reminder_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE reminders SET sent=1 WHERE id=?", (reminder_id,))


# ---------------------------------------------------------------------------
# Conversation history
# ---------------------------------------------------------------------------

def get_conversation_history(phone_number: str, limit: int = 10) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT role, content FROM conversation_history
               WHERE phone_number=?
               ORDER BY created_at DESC LIMIT ?""",
            (phone_number, limit),
        ).fetchall()
    history = [{"role": r["role"], "content": r["content"]} for r in rows]
    history.reverse()
    return history


def add_to_conversation_history(phone_number: str, role: str, content: str):
    now = datetime.now().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversation_history (phone_number, role, content, created_at) VALUES (?,?,?,?)",
            (phone_number, role, content, now),
        )
        # Keep only the 50 most recent messages per user
        conn.execute(
            """DELETE FROM conversation_history
               WHERE phone_number=? AND id NOT IN (
                   SELECT id FROM conversation_history
                   WHERE phone_number=?
                   ORDER BY created_at DESC LIMIT 50
               )""",
            (phone_number, phone_number),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _next_due_date(current_due: Optional[str], recurrence: str) -> str:
    base = (
        datetime.strptime(current_due, "%Y-%m-%d")
        if current_due
        else datetime.now()
    )
    delta = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1), "monthly": timedelta(days=30)}
    next_date = base + delta.get(recurrence, timedelta(weeks=1))
    return next_date.strftime("%Y-%m-%d")
