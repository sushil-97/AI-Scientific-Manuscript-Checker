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

failed_cases = []
evaluation_results = []
for case in cases:
    case_id = case["case_id"]
    expected = case["expected_result"]
    detector = case["detector"]


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

    if detector == "screening_flow":

        screening_flow = result[
            "sample_size_screening"
        ].get("screening_to_randomization")
        if case_id == "EVAL_006":
            print(
                "DEBUG EVAL_006 screening_flow:",
                screening_flow,
                flush=True
            )

        if (
            screening_flow is not None
            and screening_flow.get("screened") == int(case["expected_screened"])
            and screening_flow.get("randomized") == int(case["expected_randomized"])
            and screening_flow.get("difference") == int(case["expected_difference"])
            and screening_flow.get("interpretation") == "INFORMATIONAL_ONLY"
        ):
            actual = "INFORMATIONAL_ONLY"
        else:
            actual = "NOT_EVALUATED"

    elif any(
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
    if status == "FAIL":
        failed_cases.append(case_id)
    evaluation_results.append({
            "case_id": case_id,
            "expected": expected,
            "actual": actual,
            "status": status
    })

    print(
        f"{case_id} | Expected: {expected} | "
        f"Actual: {actual} | {status}",
        flush=True
    )

print("\n" + "=" * 85)
print("             MANUSCRIPT EVALUATION SUMMARY")
print("=" * 85)

print(
    f"{'Case ID':<12} "
    f"{'Expected':<25} "
    f"{'Actual':<25} "
    f"{'Status':<8}"
)

print("-" * 85)

for item in evaluation_results:
    print(
        f"{item['case_id']:<12} "
        f"{item['expected']:<25} "
        f"{item['actual']:<25} "
        f"{item['status']:<8}"
    )

print("-" * 85)

passed = sum(
    item["status"] == "PASS"
    for item in evaluation_results
)

print(f"Total Evaluated: {len(evaluation_results)}")
print(f"Passed: {passed}")
print(f"Failed: {len(failed_cases)}")

print("=" * 85, flush=True)

if failed_cases:
    raise SystemExit(
        f"Evaluation failed for: {', '.join(failed_cases)}"
    )

print("All evaluated manuscripts passed.")
