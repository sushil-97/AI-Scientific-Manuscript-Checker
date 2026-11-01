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
    print("\n===== CASE 13 DAS TEXT =====")
    print(result["das_text"])

    print("\n===== CASE 13 DATA SCREENING =====")
    print(result["data_screening"])
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
