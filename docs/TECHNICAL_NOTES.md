# Technical notes

## Data flow
The Streamlit application calls provider adapters, then pure analytics
functions. Provider I/O is isolated in `services/`; quantitative calculations
are in `analytics/` and can be tested with deterministic local fixtures.

## Data quality
- Prices are sorted chronologically and provider nulls are dropped.
- Yahoo history is requested with `auto_adjust=True`; the normalized `close`
  therefore represents adjusted close-like prices.
- News is deduplicated by link and filtered to the last configured number of
  days. Feeds can contain incomplete publication metadata; missing dates are
  stamped at collection time and should be treated cautiously.

## Financial metric conventions
The dashboard defaults to daily bars and 252 periods/year. Sharpe uses a
zero risk-free rate. Annualized return uses the first/last observed close and
the count of return intervals. These are descriptive historical metrics,
not forecasts.

## News scoring
VADER compound polarity is mapped to positive (>= 0.05), negative (<= -0.05),
or neutral. Event ranking adds fixed weights for selected headline terms to
the absolute sentiment score. It is deliberately interpretable and should
not be described as a trained event-impact model.
