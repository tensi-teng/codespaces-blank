from argus.analytics.risk_engine import calculate_risk

def test_high_risk_from_multiple_signals():
    score, level, reasons = calculate_risk(0.9, 45, 3, 40)
    assert score > 0.60 and level == 'High' and len(reasons) >= 2

def test_low_risk():
    score, level, reasons = calculate_risk(0.05, 90, 0, 75)
    assert score <= 0.30 and level == 'Low'
