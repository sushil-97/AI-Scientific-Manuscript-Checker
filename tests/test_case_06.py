import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_06_human_single_center():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_06_human_single_center.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )

    # Human study should be detected
    assert (
        result["study_characters"]
        ["human_study"]
        ["detected"]
        is True
    )

    # Ethics approval should be detected
    assert (
        result["ethics_screening"]
        ["ethics_statement_detected"]
        is True
    )

    # Consent waiver should be detected
    assert (
        result["ethics_screening"]
        ["consent_waiver_detected"]
        is True
    )

    # Accordance statement should be detected
    assert (
        result["ethics_screening"]
        ["accordance_statement_detected"]
        is True
    )

    # Ethics institution should match affiliation
    assert (
        result["ethics_screening"]
        ["affiliation_check"]
        ["status"]
        == "FULL_MATCH"
    )
        # Ethics status should pass
    assert (
        result["ethics_screening"]
        ["ethics_status"]
        == "PASS"
    )

    # Consent waiver should require editorial review
        # Consent statement should pass while
    # the waiver remains separately detected
    assert (
        result["ethics_screening"]
        ["consent_status"]
        == "PASS"
    )

    # Extracted ethics institution should be correct
    assert (
        result["ethics_screening"]
        ["affiliation_check"]
        ["ethics_institutions"]
        == ["Tianjin Beichen Hospital"]
    )

    # Institution should match the author affiliation
    assert (
        result["ethics_screening"]
        ["affiliation_check"]
        ["matched_institutions"]
        == ["Tianjin Beichen Hospital"]
    )

    # There should be no unmatched ethics institutions
    assert (
        result["ethics_screening"]
        ["affiliation_check"]
        ["unmatched_institutions"]
        == []
    )
