from app.tools.financial_extractor import extract_metrics_from_text

def test_extract_metrics():
    text = "Revenue from operations 73,188 crore. Operating margin 24.0%. Net margin 19.0%."
    result = extract_metrics_from_text(text, "fixture")
    assert result["metrics"]["revenue_inr_crore"] == "73188"
    assert result["metrics"]["operating_margin_pct"] == "24.0"
    assert result["metrics"]["net_margin_pct"] == "19.0"
