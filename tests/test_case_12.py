import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_12_sample_size_attrition():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_12_sample_size_attrition.txt"
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

    
    # Verify important participant-count roles
    extracted_counts = {
        (
            finding["numeric_value"],
            finding["role"]
        )
        for finding in sample_findings
    }

    assert (120, "ENROLLED") in extracted_counts
    assert (12, "EXCLUDED") in extracted_counts
    assert (10, "EXCLUDED") in extracted_counts
    assert (98, "ANALYZED") in extracted_counts
    assert (98, "COMPLETED") in extracted_counts

    # Enrollment-to-analysis difference should be treated
    # as participant flow, not an automatic discrepancy
    assert sample_screening["participant_flow"] == [
        {
            "enrolled_values": [120],
            "analyzed_values": [98],
            "interpretation": "INFORMATIONAL_ONLY"
        }
    ]

    # Current logic requests review because there is not
    # enough directly comparable cross-section information
    assert (
        sample_screening["status"]
        == "REVIEW"
    )
