import json
import os
import sqlite3
from datetime import datetime


DB_PATH = None


def _get_db():
    global DB_PATH
    if DB_PATH is None:
        DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history.db")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            directory TEXT NOT NULL,
            files TEXT NOT NULL,
            options TEXT NOT NULL,
            results TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


def save_entry(directory, files, options, results):
    conn = _get_db()
    conn.execute(
        "INSERT INTO history (timestamp, directory, files, options, results) VALUES (?, ?, ?, ?, ?)",
        (
            datetime.now().isoformat(),
            directory,
            json.dumps(files),
            json.dumps(options),
            json.dumps(results),
        ),
    )
    conn.commit()
    conn.close()


def list_entries(limit=20):
    conn = _get_db()
    rows = conn.execute(
        "SELECT id, timestamp, directory, files, options FROM history ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "timestamp": r["timestamp"],
            "directory": r["directory"],
            "files": json.loads(r["files"]),
            "options": json.loads(r["options"]),
        }
        for r in rows
    ]


def get_entry(entry_id):
    conn = _get_db()
    row = conn.execute("SELECT * FROM history WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "directory": row["directory"],
        "files": json.loads(row["files"]),
        "options": json.loads(row["options"]),
        "results": json.loads(row["results"]),
    }


def clear_all():
    conn = _get_db()
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()
