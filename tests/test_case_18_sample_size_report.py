from manuscript_checker import evaluate_sample_size_consistency


def test_sample_size_report_recognizes_two_arm_allocation():
    context = (
        "A total of 69 infants were assessed for eligibility "
        "and 52 infants underwent randomization with "
        "26 participants allocated to each of the "
        "“Early” and “Late” fortification arms."
    )

    findings = [
        {
            "section": "results",
            "numeric_value": 69,
            "role": "SCREENED",
            "context": context,
        },
        {
            "section": "results",
            "numeric_value": 52,
            "role": "RANDOMIZED",
            "context": context,
        },
        {
            "section": "results",
            "numeric_value": 26,
            "role": "ALLOCATED",
            "context": context,
        },
    ]

    study_characteristics = {
        "systematic_review": {"detected": False},
        "clinical_trial": {"detected": True},
        "human_study": {"detected": True},
    }

    result = evaluate_sample_size_consistency(
        study_characteristics,
        findings,
    )

    assert result["status"] == "PASS_CANDIDATE"

    allocation = result["allocation_consistency"]

    assert allocation is not None
    assert allocation["randomized"] == 52
    assert allocation["allocated_per_arm"] == 26
    assert allocation["allocated_total"] == 52
    assert allocation["result"] == "CONSISTENT"
