def test_imports():
    from argus.analytics.risk_engine import calculate_risk
    from argus.quality.validate import validate
    assert callable(calculate_risk) and callable(validate)
