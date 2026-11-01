import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_08_systematic_review():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_08_systematic_review.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )

    # Systematic review should be detected
    assert (
        result["study_characters"]
        ["systematic_review"]
        ["detected"]
        is True
    )

    # Ethics should not be required
    assert (
        result["ethics_screening"]
        ["ethics_status"]
        == "NOT_APPLICABLE"
    )

    # Consent should not be required
    assert (
        result["ethics_screening"]
        ["consent_status"]
        == "NOT_APPLICABLE"
    )
        # Negative wording should not classify this
    # systematic review as a human-participant study
    assert (
        result["study_characters"]
        ["human_study"]
        ["detected"]
        is False
    )

    # Center screening should not be triggered
    assert (
        result["center_screening"]
        ["status"]
        == "NOT_TRIGGERED"
    )

    # Sample-size consistency should not be triggered
    assert (
        result["sample_size_screening"]
        ["status"]
        == "NOT_TRIGGERED"
    )

    # Computational reproducibility should not be triggered
    assert (
        result["reproducibility_report"]
        ["status"]
        == "NOT_TRIGGERED"
    )
