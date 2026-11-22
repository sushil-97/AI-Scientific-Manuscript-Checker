
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
