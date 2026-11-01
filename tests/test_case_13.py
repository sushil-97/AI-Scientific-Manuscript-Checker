import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_13_mandated_data_missing_identifier():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_13_mandated_data_missing_identifier.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )
    
    # Data Availability screening should be generated
    assert (
        result["data_screening"]
        is not None
    )

    # DAS text should be extracted
    assert (
        result["das_text"]
        is not None
    )
        data_screening = result["data_screening"]

    # Sequencing data should trigger mandated-data screening
    assert (
        data_screening["applicability"]
        == "MANDATED"
    )

    # A Data Availability Statement should be detected
    assert (
        data_screening["statement_detected"]
        is True
    )

    # GEO should be recognized as a public repository
    assert (
        data_screening["repositories"]
        == ["geo"]
    )

    assert (
        "public_repository"
        in data_screening["access_type"]
    )

    # No accession number or persistent identifier
    # was provided in the manuscript
    assert (
        data_screening["persistent_identifiers"]
        == {}
    )

    # Mandated data in GEO without an identifier
    # should require editorial review
    assert (
        data_screening["status"]
        == "REVIEW"
    )
