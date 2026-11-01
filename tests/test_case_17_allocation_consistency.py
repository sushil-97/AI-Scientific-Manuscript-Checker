from manuscript_checker import detect_two_arm_allocation_consistency


def test_two_arm_allocation_is_consistent():
    context = (
        "A total of 69 infants were assessed for eligibility "
        "and 52 infants underwent randomization with "
        "26 participants allocated to each of the "
        "“Early” and “Late” fortification arms."
    )

    findings = [
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

    result = detect_two_arm_allocation_consistency(findings)

    assert result is not None
    assert result["randomized"] == 52
    assert result["allocated_per_arm"] == 26
    assert result["number_of_arms"] == 2
    assert result["allocated_total"] == 52
    assert result["result"] == "CONSISTENT"
