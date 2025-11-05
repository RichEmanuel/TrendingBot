# =========================================================
# modules/sentiment.py
# Provides sentiment scoring for caption text
# =========================================================

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# create one analyzer we can reuse
_analyzer = SentimentIntensityAnalyzer()

def get_sentiment_score(texts):
    """Return the average compound sentiment (-1.0 to 1.0) for a list of texts."""
    if not texts:
        return 0.0

    total = 0.0
    for t in texts:
        # Protect against non‑string values
        if not isinstance(t, str):
            continue
        result = _analyzer.polarity_scores(t)
        total += result["compound"]

    # Average across all valid texts
    avg = total / max(1, len(texts))
    return round(avg, 3)