
import csv
import subprocess
import sys
from pathlib import Path



def test_runner_rejects_invalid_strict_validation(tmp_path):
    project_root = Path(__file__).resolve().parents[1]

    original_csv = (
        project_root / "evaluation" / "evaluation_cases.csv"
    )

    with original_csv.open(
        newline="", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        cases = list(reader)

    # Modify the configuration without changing the original CSV
    cases[0]["strict_validation"] = "maybe"

    temporary_csv = tmp_path / "evaluation_cases.csv"

    with temporary_csv.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(cases)

    # Execute the actual evaluation runner
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "evaluation.run_evaluation",
            "--csv",
            str(temporary_csv)
        ],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    # Invalid configuration must cause the runner to fail
    assert result.returncode != 0

    # Verify that the failure happened for the correct reason
    output = result.stdout + result.stderr

    assert "Invalid strict_validation value" in output


def test_runner_accepts_valid_temporary_csv(tmp_path):
    project_root = Path(__file__).resolve().parents[1]

    original_csv = (
        project_root / "evaluation" / "evaluation_cases.csv"
    )

    # Copy the valid evaluation CSV to a temporary location
    temporary_csv = tmp_path / "evaluation_cases.csv"

    temporary_csv.write_bytes(
        original_csv.read_bytes()
    )

    # Execute the real evaluation runner
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "evaluation.run_evaluation",
            "--csv",
            str(temporary_csv)
        ],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    # Valid configuration should succeed
    assert result.returncode == 0, (
        result.stdout + result.stderr
    )

    # Verify the evaluation summary
    assert "10/10" in result.stdout

