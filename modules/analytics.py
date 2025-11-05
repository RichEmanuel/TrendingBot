# =========================================================
# modules/analytics.py
# Utilities that read the SQLite DB for deeper insights
# =========================================================
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("data/trends.db")

def get_top_movers(hours: int = 24, limit: int = 5):
    """
    Compare average score of each item between the older and newer half
    of the last <hours> period and return top gainers.
    """
    if not DB_PATH.exists():
        return []

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat(timespec="seconds")

    cur.execute(
        "SELECT item_name, timestamp, score FROM trends WHERE timestamp >= ? ORDER BY timestamp ASC",
        (cutoff,),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return []

    # Organize by item
    data = {}
    for name, ts, score in rows:
        data.setdefault(name, []).append(score)

    results = []
    for name, scores in data.items():
        if len(scores) < 2:
            continue
        mid = len(scores) // 2
        first_half = sum(scores[:mid]) / max(1, len(scores[:mid]))
        second_half = sum(scores[mid:]) / max(1, len(scores[mid:]))
        change = round(second_half - first_half, 2)
        results.append((name, change, second_half))

    # Sort by biggest positive change
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]