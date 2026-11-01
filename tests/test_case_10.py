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
    print("\n===== CASE 10 P-VALUE FINDINGS =====")
    print(result["pvalue_findings"])

    print("\n===== CASE 10 STATISTICAL REPORT =====")
    print(result["statistical_report"])

    # P-values should be detected
    assert len(
        result["pvalue_findings"]
    ) >= 3

    # Statistical report should be generated
    assert (
        result["statistical_report"]
        is not None
    )
