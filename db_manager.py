"""
db_manager.py
Handles all SQLite database operations:
- Search history
- Favorite words
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "smart_dict.db")


def init_db():
    """Create database tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table for search history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            searched_at TEXT NOT NULL
        )
    """)

    # Table for favorites
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL,
            added_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_to_history(word: str):
    """Add a searched word to history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (word, searched_at) VALUES (?, ?)",
        (word.lower(), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 50) -> list:
    """Retrieve recent search history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT word, searched_at FROM history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_history():
    """Delete all history records."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()


def add_to_favorites(word: str) -> bool:
    """Add a word to favorites. Returns False if already exists."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO favorites (word, added_at) VALUES (?, ?)",
            (word.lower(), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Word already in favorites


def remove_from_favorites(word: str):
    """Remove a word from favorites."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE word = ?", (word.lower(),))
    conn.commit()
    conn.close()


def get_favorites() -> list:
    """Retrieve all favorite words."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT word, added_at FROM favorites ORDER BY word ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def is_favorite(word: str) -> bool:
    """Check if a word is in favorites."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM favorites WHERE word = ?", (word.lower(),))
    result = cursor.fetchone()
    conn.close()
    return result is not None
