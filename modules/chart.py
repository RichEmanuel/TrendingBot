# =========================================================
# modules/chart.py
# Generates trend line charts from report CSVs
# =========================================================
import csv
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt

def get_history(item_name: str):
    """Return two lists: datetimes and scores for the given item."""
    report_dir = Path("data/reports")
    if not report_dir.exists():
        return [], []

    times, scores = [], []

    for file in sorted(report_dir.glob("trends_*.csv")):
        try:
            file_time = datetime.strptime(file.stem.split("_", 1)[1], "%Y-%m-%d_%H-%M-%S")
        except Exception:
            continue

        with open(file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Item"].strip().lower() == item_name.lower():
                    times.append(file_time)
                    scores.append(float(row["IntentScore"]))
    return times, scores


def make_chart(item_name: str) -> str:
    """Create a chart and return the filename."""
    x, y = get_history(item_name)
    if not x:
        return None

    plt.figure(figsize=(6, 3))
    plt.plot(x, y, marker="o", color="#00ff88")
    plt.title(f"{item_name} Trend Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Intent Score")
    plt.grid(True)
    plt.tight_layout()

    out_path = Path("data/reports") / f"{item_name.replace(' ', '_')}_trend.png"
    plt.savefig(out_path)
    plt.close()
    return str(out_path)