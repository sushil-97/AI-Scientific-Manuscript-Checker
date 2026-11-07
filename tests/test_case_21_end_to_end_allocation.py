from manuscript_checker import analyze_manuscript_text


def test_end_to_end_allocation_discrepancy():

    manuscript = """
Title
Synthetic Randomized Clinical Trial

Abstract
This randomized clinical trial investigated two treatment groups.
A total of 52 infants were randomized.

Methods
This prospective randomized clinical trial included
human participants. The study was conducted at a hospital.
Ethics approval was obtained from the institutional review board.
Informed consent was obtained from the parents.

Results
A total of 52 infants underwent randomization with
25 participants allocated to each of the
Early and Late treatment arms.

Discussion
The study compared outcomes between two treatment arms.

Data Availability
Data are available from the corresponding author
upon reasonable request.
"""

    result = analyze_manuscript_text(manuscript)

    sample_size = result["sample_size_screening"]

    assert sample_size["applicability"] == "APPLICABLE"

    allocation = sample_size["allocation_consistency"]

    assert allocation is not None
    assert allocation["randomized"] == 52
    assert allocation["allocated_per_arm"] == 25
    assert allocation["allocated_total"] == 50

    assert allocation["result"] == "POTENTIAL_DISCREPANCY"
        # Verify manuscript evidence traceability
    evidence = allocation["evidence"]

    assert evidence["section"] == "results"

    assert "52 infants underwent randomization" in evidence["text"]

    assert "25 participants allocated" in evidence["text"]

    assert "Early and Late treatment arms" in evidence["text"]

    assert sample_size["status"] == "REVIEW"

    overall = result["overall_decision"]

    assert overall["overall_status"] == "REVIEW"

    assert any(
        item["module"] == "Sample Size Consistency"
        and item["status"] == "REVIEW"
        for item in overall["review_items"]
    )

def test_end_to_end_consistent_allocation_evidence():

    manuscript = """
Title
Synthetic Randomized Clinical Trial

Abstract
This randomized clinical trial investigated two treatment groups.
A total of 52 infants were randomized.

Methods
This prospective randomized clinical trial included
human participants. The study was conducted at a hospital.
Ethics approval was obtained from the institutional review board.
Informed consent was obtained from the parents.

Results
A total of 52 infants underwent randomization with
26 participants allocated to each of the
Early and Late treatment arms.

Discussion
The study compared outcomes between two treatment arms.

Data Availability
Data are available from the corresponding author
upon reasonable request.
"""

    result = analyze_manuscript_text(manuscript)

    sample_size = result["sample_size_screening"]
    allocation = sample_size["allocation_consistency"]

    assert allocation is not None

    assert allocation["randomized"] == 52
    assert allocation["allocated_per_arm"] == 26
    assert allocation["allocated_total"] == 52

    assert allocation["result"] == "CONSISTENT"

    # Verify evidence is preserved
    evidence = allocation["evidence"]

    assert evidence["section"] == "results"
    assert "52 infants underwent randomization" in evidence["text"]
    assert "26 participants allocated" in evidence["text"]
    assert "Early and Late treatment arms" in evidence["text"]

    assert sample_size["status"] == "PASS_CANDIDATE"
