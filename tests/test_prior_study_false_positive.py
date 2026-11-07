from manuscript_checker import analyze_manuscript_text


def test_prior_study_count_not_flagged_as_discrepancy():

    manuscript = """
Title
Synthetic Randomized Clinical Trial

Abstract
A total of 120 patients were randomized.

Methods
This randomized clinical trial enrolled human participants.

Results
A previous clinical trial randomized 85 patients.
In the present study, 120 patients were randomized.

Discussion
The findings are consistent with earlier research.

Data Availability
Data are available upon reasonable request.
"""

    result = analyze_manuscript_text(manuscript)

    sample_size = result["sample_size_screening"]

    comparisons = sample_size["same_role_comparisons"]
    print("\n--- PRIOR STUDY DEBUG ---")

    for finding in result["sample_size_findings"]:
        print("Role:", finding["role"])
        print("Value:", finding["numeric_value"])
        print("Section:", finding["section"])
        print("Context:", repr(finding["context"]))
        print("-------------------------")
    
    print("\n--- SAME ROLE COMPARISONS ---")
    
    for comparison in comparisons:
        print(comparison)

    assert not any(
        comparison["role"] == "RANDOMIZED"
        and comparison["result"] == "POTENTIAL_DISCREPANCY"
        for comparison in comparisons
    )
