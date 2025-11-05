# =========================================================
# modules/mock_data.py
# Temporary example dataset for !trends command
# =========================================================

from datetime import datetime
from modules.data_structures import TrendItem

def get_mock_trends():
    """Return a sample list of TrendItem objects."""
    return [
        TrendItem(
            item_name="LED Mirror",
            hashtags=["#TikTokMadeMeBuyIt", "#RoomAesthetic"],
            caption_texts=["Love this mirror!", "Need this ASAP 🔥", "Buying one now!"],
            view_count=98000,
            like_count=8500,
            comment_count=620,
            share_count=450,
            creator_followers=20000,
            post_time=datetime.now(),
        ),
        TrendItem(
            item_name="Mini Blender",
            hashtags=["#KitchenFinds"],
            caption_texts=["I need this!", "Ordering right now", "So cute"],
            view_count=54000,
            like_count=7300,
            comment_count=480,
            share_count=210,
            creator_followers=12000,
            post_time=datetime.now(),
        ),
        TrendItem(
            item_name="Hair Curler",
            hashtags=["#BeautyTok"],
            caption_texts=["works SO well", "must have 😍", "bought mine yesterday"],
            view_count=72000,
            like_count=6400,
            comment_count=560,
            share_count=300,
            creator_followers=15000,
            post_time=datetime.now(),
        ),
    ]