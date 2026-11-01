import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript_text


def test_case_01_simulation():

    fixture_path = (
        Path(__file__).parent
        / "fixtures"
        / "case_01_simulation.txt"
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

    # Human study should not be detected
    assert (
        result["study_characters"]
        ["human_study"]
        ["detected"]
        is False
    )

    # Computational subtype should be simulation
    assert (
        result["computational_subtype"]
        ["subtype"]
        == "SIMULATION"
    )

    # Reproducibility screening should apply
    assert (
        result["reproducibility_report"]
        ["applicability"]
        == "APPLICABLE"
    )
        # Simulation reproducibility should require review
    assert (
        result["reproducibility_report"]
        ["status"]
        == "REVIEW"
    )

    # Expected reproducibility information
    # should be detected
    assert set(
        result["reproducibility_report"]
        ["reported"]
    ) == {
        "initial_conditions",
        "model_parameters",
        "software_environment"
    }

    # Missing simulation reproducibility details
    # should be identified
    assert set(
        result["reproducibility_report"]
        ["not_detected"]
    ) == {
        "numerical_solver",
        "parameter_bounds",
        "simulation_setup",
        "tolerance_settings"
    }

    # No indicators are explicitly reported
    # as unavailable
    assert (
        result["reproducibility_report"]
        ["explicitly_unavailable"]
        == []
    )
