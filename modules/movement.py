# =========================================================
# modules/movement.py
# Maintains movement icons compared with last saved report
# =========================================================
import csv
from pathlib import Path

def load_last_scores():
    """Return {item_name: last_score} from the most recent CSV, or empty dict."""
    report_dir = Path("data/reports")
    if not report_dir.exists():
        return {}

    # get all CSVs named trends_YYYY‑MM‑DD_HH‑MM‑SS.csv
    files = sorted(report_dir.glob("trends_*.csv"))
    if not files:
        return {}

    last_file = files[-1]
    scores = {}
    try:
        with open(last_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("Item")
                if not name:
                    continue
                try:
                    score = float(row.get("IntentScore", 0))
                except ValueError:
                    score = 0.0
                scores[name] = score
    except Exception as e:
        print(f"⚠️ Failed to read previous report: {e}")

    return scores


def compare_movement(current_items, previous_scores):
    """
    Return a dict {item_name: movement_icon} showing change since last run.
    """
    changes = {}
    for item in current_items:
        old = previous_scores.get(item.item_name)
        if old is None:
            changes[item.item_name] = "🆕"
        elif item.intent_score > old:
            changes[item.item_name] = "⬆️"
        elif item.intent_score < old:
            changes[item.item_name] = "⬇️"
        else:
            changes[item.item_name] = "➡️"
    return changes