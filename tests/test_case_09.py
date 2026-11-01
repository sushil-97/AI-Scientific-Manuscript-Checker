import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_09_multi_institution_partial_match():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_09_multi_institution_partial_match.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )

    affiliation_check = (
        result["ethics_screening"]
        ["affiliation_check"]
    )

    # Multiple ethics institutions should be extracted
    assert affiliation_check[
        "ethics_institutions"
    ] == [
        "Alpha University",
        "Beta University",
        "Gamma University"
    ]

    # Two institutions should match author affiliations
    assert affiliation_check[
        "matched_institutions"
    ] == [
        "Alpha University",
        "Gamma University"
    ]

    # Beta University is deliberately absent
    # from the author affiliations
    assert affiliation_check[
        "unmatched_institutions"
    ] == [
        "Beta University"
    ]

    # Mixed matching should produce PARTIAL_MATCH
    assert affiliation_check[
        "status"
    ] == "PARTIAL_MATCH"
