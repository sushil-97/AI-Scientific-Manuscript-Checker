import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_02_animal_study():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_02_animal_study.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )

    # Animal study should be detected
    assert (
        result["study_characters"]
        ["animal_study"]
        ["detected"]
        is True
    )

    # Human study should not be detected
    assert (
        result["study_characters"]
        ["human_study"]
        ["detected"]
        is False
    )

    # Systematic review should not be detected
    assert (
        result["study_characters"]
        ["systematic_review"]
        ["detected"]
        is False
    )

    # Animal studies require animal-ethics review
    assert (
        result["ethics_screening"]
        ["ethics_status"]
        == "REVIEW_ANIMAL_ETHICS"
    )

    # Human informed consent is not applicable
    assert (
        result["ethics_screening"]
        ["consent_status"]
        == "NOT_APPLICABLE"
    )
