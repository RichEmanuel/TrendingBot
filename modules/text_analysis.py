# =========================================================
# modules/text_analysis.py
# Detects desire and intent language in text data
# =========================================================

import re
from typing import List

# ------------------------------------
# 1️⃣ Intent-related keyword weights
# ------------------------------------
# Words or phrases that imply WANTING, BUYING, or NEEDING something.
# You can expand this list any time.
INTENT_KEYWORDS = {
    r"\bwant\b": 2.0,
    r"\bneed\b": 2.5,
    r"\bbuy": 2.5,
    r"\bgetting\b": 2.0,
    r"\bordered\b": 3.0,
    r"\bmust\s*have\b": 3.5,
    r"\bso\s*cute\b": 1.0,
    r"\btake\s*my\s*money\b": 4.0,
}

# ------------------------------------
# 2️⃣ Basic cleaning
# ------------------------------------
def clean_text(text: str) -> str:
    """Lowercase and remove non‑essential symbols for pattern matching."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

# ------------------------------------
# 3️⃣ Compute intent score
# ------------------------------------
def compute_intent_score(texts: List[str]) -> float:
    """
    Given a list of captions or comments, count how much 'buying desire'
    is expressed.
    Returns a numeric score (average hit weight per text).
    """
    if not texts:
        return 0.0

    total_score = 0.0
    for t in texts:
        t_clean = clean_text(t)
        for pattern, weight in INTENT_KEYWORDS.items():
            if re.search(pattern, t_clean):
                total_score += weight

    # Normalize by number of texts for consistent scaling
    avg_score = total_score / len(texts)
    return round(avg_score, 2)

# ------------------------------------
# 4️⃣ Demonstration helper
# ------------------------------------
if __name__ == "__main__":
    sample = [
        "I need this blender!",
        "Buying now 😍",
        "So cute, must have!",
    ]
    print("Sample texts:", sample)
    score = compute_intent_score(sample)
    print(f"💡 Intent score: {score}")