import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_15_durc_positive():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_15_durc_positive.txt"
    )

    manuscript_text = fixture_path.read_text(
        encoding="utf-8"
    )

    result = analyze_manuscript_text(
        manuscript_text
    )

    # DURC screening should be generated
    assert (
        result["durc_screening"]
        is not None
    )
