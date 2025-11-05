# =========================================================
# modules/insights.py
# Provides quick summaries and comparisons from SQLite data
# =========================================================
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("data/trends.db")

def get_summary(hours: int = 24):
    """
    Return (top_item, avg_score, total_items)
    summarizing the last <hours> hours of data.
    """
    if not DB_PATH.exists():
        return None

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat(timespec="seconds")

    cur.execute(
        "SELECT item_name, AVG(score) FROM trends "
        "WHERE timestamp >= ? GROUP BY item_name ORDER BY AVG(score) DESC",
        (cutoff,),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    top_item = rows[0][0]
    avg_score = sum(r[1] for r in rows) / len(rows)
    total_items = len(rows)
    return top_item, avg_score, total_items