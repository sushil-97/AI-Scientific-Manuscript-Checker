import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_12b_sample_size_discrepancy():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_12b_sample_size_discrepancy.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )
    

    # Sample-size findings should be extracted
    assert len(
        result["sample_size_findings"]
    ) >= 1

    # Sample-size screening should be generated
    assert (
        result["sample_size_screening"]
        is not None
    )
    sample_findings = result["sample_size_findings"]
    sample_screening = result["sample_size_screening"]

    # Sample-size screening should be applicable
    assert (
        sample_screening["applicability"]
        == "APPLICABLE"
    )

    # Methods should report 120 analyzed participants
    assert any(
        finding["section"] == "methods"
        and finding["numeric_value"] == 120
        and finding["role"] == "ANALYZED"
        for finding in sample_findings
    )

    # Results should report 98 analyzed participants
    assert any(
        finding["section"] == "results"
        and finding["numeric_value"] == 98
        and finding["role"] == "ANALYZED"
        for finding in sample_findings
    )

    # The same ANALYZED role should be compared
    # across Methods and Results
    assert {
        "role": "ANALYZED",
        "sections": {
            "methods": [120],
            "results": [98]
        },
        "result": "POTENTIAL_DISCREPANCY"
    } in sample_screening["same_role_comparisons"]

    # The discrepancy should require editorial review
    assert (
        sample_screening["status"]
        == "REVIEW"
    )
