from manuscript_checker import evaluate_sample_size_consistency


def test_allocation_discrepancy_takes_priority():
    context = (
        "A total of 52 infants underwent randomization "
        "with 25 participants allocated to each of the "
        "Early and Late treatment arms."
    )

    findings = [
        {
            "section": "abstract",
            "numeric_value": 52,
            "role": "RANDOMIZED",
            "context": "52 infants were randomized.",
        },
        {
            "section": "results",
            "numeric_value": 52,
            "role": "RANDOMIZED",
            "context": context,
        },
        {
            "section": "results",
            "numeric_value": 25,
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

    # The randomized count agrees across sections.
    assert any(
        item["role"] == "RANDOMIZED"
        and item["result"] == "CONSISTENT"
        for item in result["same_role_comparisons"]
    )

    # But the allocation arithmetic does not agree.
    assert result["allocation_consistency"] is not None
    assert (
        result["allocation_consistency"]["result"]
        == "POTENTIAL_DISCREPANCY"
    )

    # The discrepancy must override the consistent finding.
    assert result["status"] == "REVIEW"
