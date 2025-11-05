# =========================================================
# modules/database.py
# Handles persistent storage of trend scores in SQLite
# =========================================================
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/trends.db")

def init_db():
    """Create database and table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            item_name TEXT,
            score REAL,
            likes INTEGER,
            comments INTEGER
        )
    """)
    conn.commit()
    conn.close()


def save_trends(items):
    """Insert current list of TrendItem objects into the database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ts = datetime.now().isoformat(timespec="seconds")
    for item in items:
        cur.execute(
            "INSERT INTO trends (timestamp, item_name, score, likes, comments) VALUES (?, ?, ?, ?, ?)",
            (ts, item.item_name, item.intent_score, item.like_count, item.comment_count),
        )
    conn.commit()
    conn.close()


def query_item_history(item_name):
    """Return [(timestamp, score)] for charting or analysis."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT timestamp, score FROM trends WHERE item_name=? ORDER BY timestamp ASC",
        (item_name,),
    )
    results = cur.fetchall()
    conn.close()
    return results