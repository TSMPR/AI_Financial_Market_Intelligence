from __future__ import annotations
import numpy as np
import pandas as pd

def calculate_market_metrics(prices: pd.DataFrame, periods_per_year: int = 252) -> pd.DataFrame:
    """Compute historical metrics independently for each ticker.

    Input requires ticker, date and close columns. Daily returns are computed
    after sorting by date; missing/non-positive closes are excluded per ticker.
    Sharpe assumes a zero risk-free rate.
    """
    required = {"ticker", "date", "close"}
    if not required.issubset(prices.columns):
        raise ValueError(f"prices must contain columns: {sorted(required)}")
    rows = []
    for ticker, group in prices.groupby("ticker"):
        g = group[["date", "close"]].copy().sort_values("date")
        g["close"] = pd.to_numeric(g["close"], errors="coerce")
        g = g.dropna(subset=["close"])
        g = g[g["close"] > 0]
        returns = g["close"].pct_change().dropna()
        if len(g) < 2 or returns.empty:
            continue
        vol = float(returns.std(ddof=1) * np.sqrt(periods_per_year)) if len(returns) > 1 else np.nan
        first, last = float(g["close"].iloc[0]), float(g["close"].iloc[-1])
        n = len(returns)
        ann_return = (last / first) ** (periods_per_year / n) - 1 if n else np.nan
        daily_std = returns.std(ddof=1)
        sharpe = float(np.sqrt(periods_per_year) * returns.mean() / daily_std) if daily_std and np.isfinite(daily_std) else np.nan
        drawdown = g["close"] / g["close"].cummax() - 1
        rows.append({
            "ticker": ticker,
            "observations": len(g),
            "total_return": last / first - 1,
            "annualized_return": ann_return,
            "annualized_volatility": vol,
            "sharpe_ratio": sharpe,
            "max_drawdown": float(drawdown.min()),
        })
    return pd.DataFrame(rows)

def prepare_price_frame(raw: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Normalize yfinance output into date/ticker/close/volume columns."""
    if raw is None or raw.empty:
        return pd.DataFrame(columns=["date", "ticker", "close", "volume", "daily_return"])
    frame = raw.reset_index()
    close_col = "Adj Close" if "Adj Close" in frame.columns else "Close"
    if close_col not in frame.columns:
        raise ValueError("Provider response did not contain Close or Adj Close")
    date_col = "Date" if "Date" in frame.columns else frame.columns[0]
    out = pd.DataFrame({
        "date": pd.to_datetime(frame[date_col], errors="coerce").dt.tz_localize(None),
        "ticker": ticker,
        "close": pd.to_numeric(frame[close_col], errors="coerce"),
        "volume": pd.to_numeric(frame["Volume"], errors="coerce") if "Volume" in frame else np.nan,
    }).dropna(subset=["date", "close"]).sort_values("date")
    out["daily_return"] = out["close"].pct_change()
    return out.reset_index(drop=True)
