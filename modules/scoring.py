# =========================================================
# modules/scoring.py
# Combines keyword intent, engagement, and sentiment scores
# =========================================================

from modules.data_structures import TrendItem
from modules.text_analysis import compute_intent_score
from modules.sentiment import get_sentiment_score


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
    engagement_factor = (
        (item.like_count + item.comment_count + item.share_count)
        / max(1, item.view_count)
    ) * 5

    # --- 3️⃣ Sentiment multiplier ---
    sentiment = get_sentiment_score(item.caption_texts)  # range −1 to +1
    sentiment_multiplier = max(0, 1 + sentiment)  # neutral = 1 ×, positive > 1, negative < 1

    # --- 4️⃣ Final score ---
    final_score = (lang_score + engagement_factor) * sentiment_multiplier
    item.intent_score = round(final_score, 2)
    return item


# =========================================================
# Stand‑alone test  →  python -m modules.scoring
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