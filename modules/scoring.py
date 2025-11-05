# =========================================================
# modules/scoring.py
# Weighted combination of keyword intent, engagement, and sentiment
# =========================================================
import json
import os
from modules.data_structures import TrendItem
from modules.text_analysis import compute_intent_score
from modules.sentiment import get_sentiment_score

# ---------------------------------------------------------
#  Load weights from data/config.json  (fallbacks if missing)
# ---------------------------------------------------------
try:
    with open(os.path.join("data", "config.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)
        WEIGHT_LANGUAGE = cfg.get("WEIGHT_LANGUAGE", 0.6)
        WEIGHT_ENGAGEMENT = cfg.get("WEIGHT_ENGAGEMENT", 0.3)
        WEIGHT_SENTIMENT = cfg.get("WEIGHT_SENTIMENT", 0.1)
except Exception:
    WEIGHT_LANGUAGE = 0.6
    WEIGHT_ENGAGEMENT = 0.3
    WEIGHT_SENTIMENT = 0.1

# =========================================================
#  Core function
# =========================================================
def update_intent_score(item: TrendItem) -> TrendItem:
    """
    Calculate and update Intent Score for a TrendItem.
    Components:
      1. Keyword intent signal
      2. Engagement weighting
      3. Sentiment adjustment
    """

    # --- 1️⃣ Keyword intent ---
    lang_score = compute_intent_score(item.caption_texts)

    # --- 2️⃣ Engagement factor (per‑view normalization) ---
    engagement_rate = (
        (item.like_count + item.comment_count + item.share_count)
        / max(1, item.view_count)
    ) * 100  # convert to percent for even scaling

    # --- 3️⃣ Sentiment raw value (−1 to +1) ---
    sentiment_raw = get_sentiment_score(item.caption_texts)
    sentiment_norm = (sentiment_raw + 1) * 50  # shift to 0–100 scale

    # --- 4️⃣ Weighted combo ---
    total = (
        lang_score * WEIGHT_LANGUAGE
        + engagement_rate * WEIGHT_ENGAGEMENT
        + sentiment_norm * WEIGHT_SENTIMENT
    )

    item.intent_score = round(total, 2)
    return item

# =========================================================
#  Stand‑alone test  →  python ‑m modules.scoring
# =========================================================
if __name__ == "__main__":
    from datetime import datetime

    dummy = TrendItem(
        item_name="Mini Blender",
        hashtags=["#TikTokMadeMeBuyIt"],
        caption_texts=[
            "I need this blender!",
            "Love this thing 😍",
            "Buying immediately!",
        ],
        view_count=54000,
        like_count=7300,
        comment_count=480,
        share_count=210,
        creator_followers=12000,
        post_time=datetime.now(),
    )

    updated = update_intent_score(dummy)
    print("🧩 Updated item summary:", updated.summary())
    print(
        f"Weights → Lang:{WEIGHT_LANGUAGE}, Eng:{WEIGHT_ENGAGEMENT}, Sent:{WEIGHT_SENTIMENT}"
    )