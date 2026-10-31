from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import streamlit as st
import pandas as pd
import plotly.express as px
from market_intelligence.config import Settings
from market_intelligence.services.market_data import MarketDataService
from market_intelligence.services.news import NewsService
from market_intelligence.analytics.metrics import calculate_market_metrics
from market_intelligence.analytics.events import rank_market_events
from market_intelligence.services.reporting import build_daily_report

st.set_page_config(page_title="Market Intelligence", page_icon="📈", layout="wide")
st.title("📈 AI-Powered Financial Market Intelligence")
st.caption("Research workspace for market data, financial news, sentiment and risk context.")
settings = Settings.from_env()
with st.sidebar:
    st.header("Research settings")
    tickers_text = st.text_input("Ticker symbols", "AAPL, MSFT, NVDA")
    period = st.selectbox("Historical period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    interval = st.selectbox("Data interval", ["1d", "1wk"], index=0)
    news_limit = st.slider("Maximum news articles", 10, 100, 30, 5)
    st.caption("Data providers: Yahoo Finance (via yfinance) and public RSS feeds.")
    refresh = st.button("Refresh research", type="primary", use_container_width=True)

tickers = list(dict.fromkeys(t.strip().upper() for t in tickers_text.split(",") if t.strip()))
if not tickers:
    st.warning("Enter at least one ticker symbol.")
    st.stop()

@st.cache_data(ttl=900, show_spinner=False)
def load_market(symbols, p, i):
    return MarketDataService().fetch_many(list(symbols), period=p, interval=i)

@st.cache_data(ttl=900, show_spinner=False)
def load_news(symbols, limit):
    return NewsService().fetch_news(list(symbols), limit=limit)

if refresh:
    st.cache_data.clear()

with st.spinner("Collecting market data and financial headlines..."):
    try:
        prices = load_market(tuple(tickers), period, interval)
    except Exception as exc:
        st.error(f"Market data collection failed: {exc}")
        st.stop()
    try:
        news = load_news(tuple(tickers), news_limit)
    except Exception as exc:
        st.warning(f"News collection failed: {exc}")
        news = pd.DataFrame()

if prices.empty:
    st.error("No price data returned. Check ticker symbols and network access.")
    st.stop()

metrics = calculate_market_metrics(prices, periods_per_year=52 if interval == '1wk' else 252)
latest = prices.sort_values("date").groupby("ticker").tail(1)
cols = st.columns(min(4, len(tickers)))
for idx, (_, row) in enumerate(latest.head(4).iterrows()):
    with cols[idx]:
        st.metric(row["ticker"], f"{row['close']:,.2f}", f"{row['daily_return']*100:+.2f}%" if pd.notna(row["daily_return"]) else None)

tab1, tab2, tab3, tab4 = st.tabs(["Market overview", "News & sentiment", "Event monitor", "Daily report"])
with tab1:
    st.subheader("Adjusted closing price")
    fig = px.line(prices, x="date", y="close", color="ticker", title="Historical closing prices")
    fig.update_layout(legend_title_text="Ticker", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Risk and return snapshot")
    if not metrics.empty:
        st.dataframe(metrics.style.format({"total_return":"{:.2%}", "annualized_volatility":"{:.2%}", "annualized_return":"{:.2%}", "max_drawdown":"{:.2%}", "sharpe_ratio":"{:.2f}"}), use_container_width=True)
    returns = prices.pivot(index="date", columns="ticker", values="daily_return")
    corr = returns.corr(min_periods=10)
    if not corr.empty:
        st.plotly_chart(px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu", title="Daily-return correlation"), use_container_width=True)
with tab2:
    st.subheader("Financial news")
    if news.empty:
        st.info("No RSS headlines available right now. Market analytics remain available.")
    else:
        sentiment_counts = news["sentiment_label"].value_counts().rename_axis("sentiment").reset_index(name="articles")
        st.plotly_chart(px.bar(sentiment_counts, x="sentiment", y="articles", title="Headline sentiment distribution"), use_container_width=True)
        for _, item in news.sort_values("published", ascending=False).iterrows():
            st.markdown(f"**[{item['title']}]({item['link']})**")
            st.caption(f"{item['source']} · {item['published']} · {item['sentiment_label']} ({item['sentiment_score']:+.2f})")
            if item.get("summary"):
                st.write(str(item["summary"])[:500])
            st.divider()
with tab3:
    st.subheader("Potential market-moving headlines")
    events = rank_market_events(news)
    if events.empty:
        st.info("No news events to rank. Try refreshing later.")
    else:
        st.dataframe(events[["ticker", "published", "event_score", "sentiment_label", "title", "link"]], use_container_width=True, hide_index=True,
                     column_config={"link": st.column_config.LinkColumn("Article")})
        st.caption("Event score is a transparent heuristic based on headline language and sentiment, not a causal impact estimate.")
with tab4:
    st.subheader("Research note")
    report = build_daily_report(prices, news, metrics, tickers)
    st.markdown(report)
    st.download_button("Download Markdown report", report, file_name="daily_market_intelligence_report.md", mime="text/markdown")
    if not news.empty:
        st.download_button("Download news CSV", news.to_csv(index=False), file_name="financial_news.csv", mime="text/csv")
    st.download_button("Download market data CSV", prices.to_csv(index=False), file_name="market_data.csv", mime="text/csv")

with st.expander("Data notes and responsible use"):
    st.write("Market prices and headlines are retrieved from third-party public sources and may be delayed, revised, incomplete or unavailable. Sentiment and event scores are heuristic research aids, not investment recommendations.")
