
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
    
    assert "Total Evaluated: 10" in result.stdout
    assert "Passed: 10" in result.stdout
    assert "Failed: 0" in result.stdout
    assert "Pass Rate: 100.00%" in result.stdout


def test_runner_reports_correct_eval_002_result(tmp_path):
    project_root = Path(__file__).resolve().parents[1]

    original_csv = (
        project_root / "evaluation" / "evaluation_cases.csv"
    )

    temporary_csv = tmp_path / "evaluation_cases.csv"
    temporary_csv.write_bytes(original_csv.read_bytes())

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

    assert result.returncode == 0, (
        result.stdout + result.stderr
    )

    # Verify the individual evaluation result
    
    eval_002_lines = [
        line for line in result.stdout.splitlines()
        if line.strip().startswith("EVAL_002 ")
        and "|" not in line
    ]


    assert len(eval_002_lines) == 1

    columns = eval_002_lines[0].split()

    assert columns == [
        "EVAL_002",
        "POTENTIAL_DISCREPANCY",
        "POTENTIAL_DISCREPANCY",
        "PASS",
    ]


def test_runner_detects_incorrect_expected_result(tmp_path):
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

    # Intentionally change EVAL_002's expected result
    for case in cases:
        if case["case_id"] == "EVAL_002":
            case["expected_result"] = "CONSISTENT"
            break
    else:
        raise AssertionError("EVAL_002 not found")

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

    # The runner must reject the incorrect expectation
    assert result.returncode != 0

    # Verify the case was reported as failed
    
# Find the EVAL_002 row in the summary table
    eval_002_lines = [
        line for line in result.stdout.splitlines()
        if line.strip().startswith("EVAL_002 ")
        and "|" not in line
    ]
    
    assert len(eval_002_lines) == 1
    
    columns = eval_002_lines[0].split()
    

    assert columns == [
        "EVAL_002",
        "CONSISTENT",
        "CLASSIFICATION_MISMATCH",
        "FAIL",
    ]

    
    # Verify the overall failure count
    assert "Failed: 1" in result.stdout




