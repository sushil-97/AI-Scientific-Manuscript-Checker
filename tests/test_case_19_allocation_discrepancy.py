from manuscript_checker import detect_two_arm_allocation_consistency


def test_two_arm_allocation_discrepancy():
    context = (
        "A total of 52 infants underwent randomization "
        "with 25 participants allocated to each of the "
        "Early and Late treatment arms."
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
            "numeric_value": 25,
            "role": "ALLOCATED",
            "context": context,
        },
    ]

    result = detect_two_arm_allocation_consistency(findings)

    assert result is not None
    assert result["randomized"] == 52
    assert result["allocated_per_arm"] == 25
    assert result["allocated_total"] == 50
    assert result["result"] == "POTENTIAL_DISCREPANCY"
