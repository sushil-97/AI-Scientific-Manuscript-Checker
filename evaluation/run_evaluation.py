from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from manuscript_checker import analyze_manuscript
import csv

# Locate evaluation files
BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "evaluation_cases.csv"
MANUSCRIPT_DIR = BASE_DIR / "manuscripts"

# Load evaluation labels
with open(CSV_PATH, "r", encoding="utf-8") as file:
    cases = list(csv.DictReader(file))

print("Evaluation cases loaded:", len(cases))


for case in cases:
    case_id = case["case_id"]
    expected = case["expected_result"]


    manuscript_path = MANUSCRIPT_DIR / f"{case_id}.txt"
    print(
        f"DEBUG: {case_id} | "
        f"Path: {manuscript_path} | "
        f"Exists: {manuscript_path.exists()}",
        flush=True
    )

    if not manuscript_path.exists():
        print(f"{case_id} | SKIPPED: Manuscript not created yet")
        continue

    result = analyze_manuscript(str(manuscript_path))
    

    comparisons = result[
        "sample_size_screening"
    ]["same_role_comparisons"]

    randomized_comparisons = [
        comparison
        for comparison in comparisons
        if comparison["role"] == "RANDOMIZED"
    ]

    if any(
        comparison["result"] == "POTENTIAL_DISCREPANCY"
        for comparison in randomized_comparisons
    ):
        actual = "POTENTIAL_DISCREPANCY"

    elif any(
        comparison["result"] == "CONSISTENT"
        for comparison in randomized_comparisons
    ):
        actual = "CONSISTENT"

    else:
        actual = "NOT_EVALUATED"

    status = "PASS" if actual == expected else "FAIL"

    print(
        f"{case_id} | Expected: {expected} | "
        f"Actual: {actual} | {status}",
        flush=True
    )
