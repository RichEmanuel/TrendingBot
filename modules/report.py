# =========================================================
# modules/report.py
# Saves each leaderboard to data/reports/
# =========================================================
import csv
from datetime import datetime
from pathlib import Path

def save_report(items):
    """Write a timestamped CSV of current trend list."""
    report_dir = Path("data/reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    filename = report_dir / f"trends_{datetime.now():%Y-%m-%d_%H-%M-%S}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Item", "IntentScore", "Likes", "Comments"])
        for idx, item in enumerate(items, start=1):
            writer.writerow([idx, item.item_name, item.intent_score,
                             item.like_count, item.comment_count])

    print(f"💾 saved report → {filename}")
    return filename