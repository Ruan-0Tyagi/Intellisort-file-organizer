"""
database/history.py
--------------------
Job: Record every file move in a SQLite database, and provide a way
to undo the most recent organize session by reversing those moves.
"""

import sqlite3
import time
from pathlib import Path

DB_FILENAME = "intellisort_history.db"


def get_db_path(target_folder: Path) -> Path:
    return target_folder / DB_FILENAME


def init_db(target_folder: Path):
    """Creates the database and table if they don't already exist."""
    db_path = get_db_path(target_folder)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            original_path TEXT NOT NULL,
            new_path TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def new_session_id() -> str:
    """Creates a unique ID for this organize run, based on current time."""
    return str(int(time.time()))


def log_move(target_folder: Path, session_id: str, original_path: Path, new_path: Path):
    """Records one file move into the database."""
    db_path = get_db_path(target_folder)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO moves (session_id, original_path, new_path, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, str(original_path), str(new_path), time.time()),
    )
    conn.commit()
    conn.close()


def get_last_session_id(target_folder: Path) -> str | None:
    """Finds the most recent session ID, or None if there's no history yet."""
    db_path = get_db_path(target_folder)
    if not db_path.exists():
        return None

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT session_id FROM moves ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    conn.close()

    return row[0] if row else None


def undo_session(target_folder: Path, session_id: str) -> int:
    """
    Moves every file from this session back to its original location.
    Returns the number of files restored.
    """
    import shutil

    db_path = get_db_path(target_folder)
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT id, original_path, new_path FROM moves WHERE session_id = ? ORDER BY id DESC",
        (session_id,),
    ).fetchall()

    restored_count = 0

    for row_id, original_path, new_path in rows:
        new_path = Path(new_path)
        original_path = Path(original_path)

        if new_path.exists():
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(new_path), str(original_path))
            restored_count += 1

        conn.execute("DELETE FROM moves WHERE id = ?", (row_id,))

    conn.commit()
    conn.close()

    for item in target_folder.iterdir():
        if item.is_dir() and not any(item.iterdir()):
            item.rmdir()

    return restored_count