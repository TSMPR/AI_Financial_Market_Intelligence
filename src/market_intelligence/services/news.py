from __future__ import annotations
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus
import feedparser
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from market_intelligence.utils.logging_config import get_logger

logger = get_logger(__name__)
ANALYZER = SentimentIntensityAnalyzer()

class NewsService:
    """Collect headlines from Google News RSS search feeds; no API key required."""
    def __init__(self, timeout_seconds: int = 15, max_age_days: int = 14):
        self.timeout_seconds = timeout_seconds
        self.max_age_days = max_age_days

    def _feed_url(self, ticker: str) -> str:
        query = quote_plus(f"{ticker} stock")
        return f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    @staticmethod
    def _published(entry) -> datetime:
        parsed = entry.get("published_parsed") or entry.get("updated_parsed")
        if parsed:
            from time import mktime
            return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
        return datetime.now(timezone.utc)

    def fetch_news(self, tickers: list[str], limit: int = 30) -> pd.DataFrame:
        rows, seen = [], set()
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.max_age_days)
        for ticker in dict.fromkeys(t.upper() for t in tickers if t.strip()):
            try:
                feed = feedparser.parse(self._feed_url(ticker), request_headers={"User-Agent": "MarketIntelligenceResearch/1.0"})
                if getattr(feed, "bozo", False):
                    logger.warning("RSS feed parsing warning for %s: %s", ticker, getattr(feed, "bozo_exception", "unknown"))
                for entry in feed.entries:
                    link = entry.get("link", "")
                    title = entry.get("title", "").strip()
                    if not title or (link and link in seen):
                        continue
                    published = self._published(entry)
                    if published < cutoff:
                        continue
                    seen.add(link)
                    summary = entry.get("summary", "")
                    text = f"{title}. {summary}"
                    compound = ANALYZER.polarity_scores(text)["compound"]
                    label = "positive" if compound >= 0.05 else "negative" if compound <= -0.05 else "neutral"
                    rows.append({
                        "ticker": ticker, "title": title, "summary": summary,
                        "link": link, "source": entry.get("source", {}).get("title", "Google News RSS"),
                        "published": published.isoformat(), "sentiment_score": float(compound),
                        "sentiment_label": label,
                    })
            except Exception:
                logger.exception("News feed failed for %s", ticker)
        if not rows:
            return pd.DataFrame(columns=["ticker","title","summary","link","source","published","sentiment_score","sentiment_label"])
        frame = pd.DataFrame(rows).sort_values("published", ascending=False)
        return frame.head(max(1, int(limit))).reset_index(drop=True)
