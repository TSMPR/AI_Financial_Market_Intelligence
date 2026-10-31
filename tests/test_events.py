import pandas as pd
from market_intelligence.analytics.events import rank_market_events

def test_event_ranking_prioritizes_earnings_keyword():
    frame = pd.DataFrame([
        {"ticker":"AAA", "title":"Company reports earnings beats", "sentiment_score":0.3, "published":"2024-01-01"},
        {"ticker":"BBB", "title":"A quiet market update", "sentiment_score":0.0, "published":"2024-01-02"},
    ])
    result = rank_market_events(frame)
    assert result.iloc[0]["ticker"] == "AAA"
    assert result.iloc[0]["event_score"] > result.iloc[1]["event_score"]

def test_empty_news_safe():
    assert rank_market_events(pd.DataFrame()).empty
