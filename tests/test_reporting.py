import pandas as pd
from market_intelligence.services.reporting import build_daily_report

def test_report_handles_empty_inputs():
    report = build_daily_report(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), ["AAPL"])
    assert "Daily Financial Market Intelligence Report" in report
    assert "AAPL" in report
