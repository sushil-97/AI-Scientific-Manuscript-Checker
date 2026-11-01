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
