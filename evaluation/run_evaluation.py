from pathlib import Path
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
        f"{case_id} | Expected: {expected} | "
        f"File exists: {manuscript_path.exists()}"
    )
