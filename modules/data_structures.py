# =========================================================
# modules/data_structures.py
# Defines the core data blueprint for a trending item
# =========================================================

from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class TrendItem:
    """
    Represents one trending product or item detected on TikTok.
    Each instance holds the key metrics and text data used later
    for scoring desirability and tracking growth.
    """

    # --- Basic identifying information ---
    item_name: str                 # e.g. 'Mini Blender'
    hashtags: List[str]            # e.g. ['#TikTokMadeMeBuyIt', '#KitchenFinds']

    # --- Text content to analyze ---
    caption_texts: List[str]       # captions and/or comments

    # --- Engagement metrics (quantitative) ---
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    creator_followers: int         # creator's audience size

    # --- Time-related metadata ---
    post_time: datetime            # timestamp when the content was posted

    # --- Computed analytics ---
    intent_score: float = 0.0      # measure of how much people “want” it (to be filled later)

    # -----------------------------------------------------
    # Utility methods
    # -----------------------------------------------------
    def summary(self) -> str:
        """Return a neat one‑line summary for display in logs or Discord."""
        return (
            f"{self.item_name} | "
            f"Likes: {self.like_count:,} | "
            f"Comments: {self.comment_count:,} | "
            f"Score: {self.intent_score:.2f}"
        )

    def as_dict(self) -> dict:
        """Convert the dataclass into a plain dictionary (useful for JSON export)."""
        return {
            "item_name": self.item_name,
            "hashtags": self.hashtags,
            "caption_texts": self.caption_texts,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "share_count": self.share_count,
            "creator_followers": self.creator_followers,
            "post_time": self.post_time.isoformat(),
            "intent_score": self.intent_score,
        }