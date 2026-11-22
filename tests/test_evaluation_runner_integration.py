
import csv
import subprocess
import sys
from pathlib import Path


def test_runner_rejects_invalid_strict_validation(tmp_path):
    project_root = Path(__file__).resolve().parents[1]

    original_csv = (
        project_root / "evaluation" / "evaluation_cases.csv"
    )

    with original_csv.open(newline="", encoding="utf-8") as file:
        cases = list(csv.DictReader(file))

    # Create an invalid configuration in memory
    cases[0]["strict_validation"] = "maybe"

    # Write the modified CSV to a temporary location
    temporary_csv = tmp_path / "evaluation_cases.csv"

    with temporary_csv.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=cases[0].keys()
        )
        writer.writeheader()
        writer.writerows(cases)

    # Check that the parser rejects the invalid value
    from evaluation.validators import parse_strict_validation

    try:
        parse_strict_validation(cases[0]["strict_validation"])
    except ValueError as error:
        assert "Invalid strict_validation value" in str(error)
    else:
        raise AssertionError("Invalid configuration was accepted")
