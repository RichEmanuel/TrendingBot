# =========================================================
# modules/sources/tiktok_loader.py
# =========================================================
import json
from pathlib import Path

def get_latest_trends():
    """
    Temporary loader that reads data/trends.json.
    Replace this with a real API request later.
    """
    try:
        file_path = Path("data/trends.json")
        if not file_path.exists():
            print("⚠️  trends.json not found – returning empty list.")
            return []
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            print("⚠️  trends.json does not contain a list.")
            return []
    except Exception as e:
        print("⚠️  Error loading trends.json:", e)
        return []