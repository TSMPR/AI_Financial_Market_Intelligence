import pandas as pd
import pytest
from market_intelligence.analytics.metrics import calculate_market_metrics

def test_metrics_known_values_and_drawdown():
    frame = pd.DataFrame({
        "ticker": ["XYZ"] * 4,
        "date": pd.date_range("2024-01-01", periods=4),
        "close": [100, 110, 99, 121],
    })
    result = calculate_market_metrics(frame).iloc[0]
    assert result["total_return"] == pytest.approx(0.21)
    assert result["max_drawdown"] == pytest.approx(-0.10)
    assert result["observations"] == 4

def test_empty_input_returns_empty_frame():
    frame = pd.DataFrame(columns=["ticker", "date", "close"])
    assert calculate_market_metrics(frame).empty

def test_missing_required_column_raises():
    with pytest.raises(ValueError):
        calculate_market_metrics(pd.DataFrame({"ticker": ["A"]}))
