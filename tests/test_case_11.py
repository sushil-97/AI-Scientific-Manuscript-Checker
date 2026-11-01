import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_11_ml_nlp():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_11_ml_nlp.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )
    

    # Computational study should be detected
    assert (
        result["study_characters"]
        ["computational_study"]
        ["detected"]
        is True
    )

    # Explicit negative wording should prevent
    # classification as a human-participant study
    assert (
        result["study_characters"]
        ["human_study"]
        ["detected"]
        is False
    )

    # Computational subtype should be ML/NLP
    assert (
        result["computational_subtype"]
        ["subtype"]
        == "ML_NLP"
    )
        # Data Availability Statement should be detected
    assert (
        result["data_screening"]
        ["statement_detected"]
        is True
    )

    # GitHub should be recognized as a repository
    assert (
        result["data_screening"]
        ["repositories"]
        == ["github"]
    )

    # Repository access should be classified as public
    assert (
        "public_repository"
        in result["data_screening"]
        ["access_type"]
    )

    # Data availability should pass screening
    assert (
        result["data_screening"]
        ["status"]
        == "PASS_CANDIDATE"
    )

    # Computational reproducibility should apply
    assert (
        result["reproducibility_report"]
        ["applicability"]
        == "APPLICABLE"
    )

    # Required ML/NLP reproducibility indicators
    # should all be detected
    assert set(
        result["reproducibility_report"]
        ["reported"]
    ) == {
        "code_availability",
        "evaluation_metrics",
        "software_environment"
    }

    # No required reproducibility indicators
    # should be missing
    assert (
        result["reproducibility_report"]
        ["not_detected"]
        == []
    )

    # Reproducibility screening should pass
    assert (
        result["reproducibility_report"]
        ["status"]
        == "PASS_CANDIDATE"
    )
