from __future__ import annotations
from datetime import datetime, timezone
import pandas as pd

def build_daily_report(prices: pd.DataFrame, news: pd.DataFrame, metrics: pd.DataFrame, tickers: list[str]) -> str:
    lines = [
        "# Daily Financial Market Intelligence Report",
        f"\nGenerated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"\nWatchlist: {', '.join(tickers)}",
        "\n> Research only. Historical data and heuristic sentiment are not investment advice.",
        "\n## Market snapshot",
    ]
    if prices is None or prices.empty:
        lines.append("\nNo market data was returned.")
    else:
        latest = prices.sort_values("date").groupby("ticker").tail(1)
        for _, row in latest.iterrows():
            ret = row.get("daily_return")
            ret_text = f"{ret:.2%}" if pd.notna(ret) else "n/a"
            lines.append(f"\n- **{row['ticker']}**: close {row['close']:.2f}; latest observed daily return {ret_text} ({row['date']:%Y-%m-%d}).")
    lines.append("\n## Historical risk and return")
    if metrics is None or metrics.empty:
        lines.append("\nInsufficient observations to calculate metrics.")
    else:
        for _, row in metrics.iterrows():
            lines.append(
                f"\n- **{row['ticker']}**: total return {row['total_return']:.2%}; "
                f"annualized volatility {row['annualized_volatility']:.2%}; "
                f"Sharpe (zero risk-free rate) {row['sharpe_ratio']:.2f}; "
                f"maximum drawdown {row['max_drawdown']:.2%}."
            )
    lines.append("\n## News sentiment")
    if news is None or news.empty:
        lines.append("\nNo recent RSS headlines were available.")
    else:
        counts = news["sentiment_label"].value_counts()
        lines.append("\nArticle counts: " + ", ".join(f"{k} {v}" for k, v in counts.items()) + ".")
        for _, row in news.head(10).iterrows():
            lines.append(f"\n- [{row['title']}]({row['link']}) — {row['ticker']}, {row['sentiment_label']} ({row['sentiment_score']:+.2f}).")
    lines.append("\n## Interpretation notes\n")
    lines.append("Sentiment is lexicon-based and the event monitor is a keyword heuristic. Neither establishes causation or predicts price movement. Validate important claims against original filings and publisher articles.")
    return "\n".join(lines)
