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
    print("\n===== CASE 10B P-VALUE FINDINGS =====")
    print(result["pvalue_findings"])

    print("\n===== CASE 10B STATISTICAL REPORT =====")
    print(result["statistical_report"])

    # Basic smoke checks first
    assert len(
        result["pvalue_findings"]
    ) >= 1

    assert (
        result["statistical_report"]
        is not None
    )
