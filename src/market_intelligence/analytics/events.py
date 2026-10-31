from __future__ import annotations
import pandas as pd

EVENT_TERMS = {
    "earnings": 1.5, "guidance": 1.5, "forecast": 1.2, "acquisition": 1.5,
    "merger": 1.5, "lawsuit": 1.3, "investigation": 1.4, "fda": 1.5,
    "recall": 1.2, "bankruptcy": 1.7, "default": 1.5, "layoff": 1.0,
    "ceo": 0.8, "downgrade": 1.0, "upgrade": 1.0, "misses": 1.1,
    "beats": 1.1, "halt": 1.4, "fraud": 1.5, "rate decision": 1.2,
}

def rank_market_events(news: pd.DataFrame) -> pd.DataFrame:
    """Rank headlines using transparent keyword and sentiment magnitude weights."""
    if news is None or news.empty:
        return pd.DataFrame(columns=list(news.columns) + ["event_score"] if news is not None else ["event_score"])
    out = news.copy()
    def score(row):
        title = str(row.get("title", "")).lower()
        keyword_score = sum(weight for term, weight in EVENT_TERMS.items() if term in title)
        sentiment = abs(float(row.get("sentiment_score", 0) or 0))
        return round(keyword_score + sentiment, 3)
    out["event_score"] = out.apply(score, axis=1)
    return out.sort_values(["event_score", "published"], ascending=[False, False]).reset_index(drop=True)
