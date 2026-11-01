import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_10b_statistical_discrepancy():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_10b_statistical_discrepancy.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )
    print("\n===== CASE 10B OVERALL DECISION =====")
    print(result["overall_decision"])
    

    # Basic smoke checks first
    assert len(
        result["pvalue_findings"]
    ) >= 1

    assert (
        result["statistical_report"]
        is not None
    )
    statistical_report = result["statistical_report"]

    # The contradictory Results p-value should be detected
    assert statistical_report["results_pvalues"] == [
        0.21
    ]

    # The manuscript makes a significant claim
    assert statistical_report["results_claims"] == [
        "SIGNIFICANT"
    ]

    # The local claim and p-value should be checked together
    assert statistical_report["claim_pvalue_checks"] == [
        {
            "section": "results",
            "claim": "SIGNIFICANT",
            "pvalue": 0.21,
            "result": "DISCREPANCY"
        }
    ]

    # The contradiction must affect the final statistical status
    assert (
        statistical_report["status"]
        == "DISCREPANCY"
    )
