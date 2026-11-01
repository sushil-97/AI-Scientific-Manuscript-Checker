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
    print("\n===== CASE 11 DATA SCREENING =====")
    print(result["data_screening"])

    print("\n===== CASE 11 REPRODUCIBILITY =====")
    print(result["reproducibility_report"])

    print("\n===== CASE 11 REPOSITORY / DAS =====")
    print("DAS:", result["das_text"])

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
