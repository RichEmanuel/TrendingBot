# =========================================================
# modules/sources/update_cache.py
# =========================================================
import json
from datetime import datetime
from modules.sources.tiktok_loader import get_latest_trends


def update_local_cache():
    """
    Refresh the local trends cache.
    Currently calls get_latest_trends() and writes
    the result to data/trends_cache.json.
    """
    try:
        data = get_latest_trends()
        with open("data/trends_cache.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"🗂  Local cache updated at {datetime.now():%Y-%m-%d %H:%M}")
    except Exception as e:
        print("⚠️  Unable to update cache:", e)