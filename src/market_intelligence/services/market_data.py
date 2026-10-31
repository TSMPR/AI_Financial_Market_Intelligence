from __future__ import annotations
import yfinance as yf
import pandas as pd
from market_intelligence.analytics.metrics import prepare_price_frame
from market_intelligence.utils.logging_config import get_logger

logger = get_logger(__name__)

class MarketDataService:
    def fetch_ticker(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        symbol = ticker.strip().upper()
        if not symbol:
            raise ValueError("Ticker cannot be blank")
        try:
            raw = yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=True)
        except Exception as exc:
            logger.exception("Failed to fetch %s", symbol)
            raise RuntimeError(f"Could not retrieve market data for {symbol}: {exc}") from exc
        if raw is None or raw.empty:
            logger.warning("No market history returned for %s", symbol)
            return prepare_price_frame(pd.DataFrame(), symbol)
        return prepare_price_frame(raw, symbol)

    def fetch_many(self, tickers: list[str], period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        frames = [self.fetch_ticker(t, period, interval) for t in dict.fromkeys(tickers)]
        nonempty = [f for f in frames if not f.empty]
        if not nonempty:
            return pd.DataFrame(columns=["date", "ticker", "close", "volume", "daily_return"])
        return pd.concat(nonempty, ignore_index=True).sort_values(["ticker", "date"]).reset_index(drop=True)
