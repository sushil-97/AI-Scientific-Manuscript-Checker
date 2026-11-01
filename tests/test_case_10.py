import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_10_statistical_consistency():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_10_statistical_consistency.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )
   

    # P-values should be detected
    assert len(
        result["pvalue_findings"]
    ) >= 3

    # Statistical report should be generated
    assert (
        result["statistical_report"]
        is not None
    )
        # Statistical report should identify all Results p-values
    assert set(
        result["statistical_report"]["results_pvalues"]
    ) == {
        0.018,
        0.032,
        0.21
    }

    # Current implementation uses the default significance threshold
    assert (
        result["statistical_report"]["significance_threshold"]
        == 0.05
    )

    assert (
        result["statistical_report"]["threshold_detected"]
        is False
    )

    assert (
        result["statistical_report"]["threshold_source"]
        == "default"
    )

    # Both significant and non-significant claims are present
    assert set(
        result["statistical_report"]["results_claims"]
    ) == {
        "SIGNIFICANT",
        "NOT_SIGNIFICANT"
    }

    # No statistical discrepancy should be raised
    assert (
        result["statistical_report"]["status"]
        == "PASS_CANDIDATE"
    )

    # Cross-section consistency cannot be assessed
    # because no corresponding abstract claims were detected
    assert (
        result["statistical_report"]["claim_consistency"]
        == "NOT_ASSESSABLE"
    )
