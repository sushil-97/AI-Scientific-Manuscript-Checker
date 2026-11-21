from manuscript_checker import detect_screening_to_randomization_flow


def test_randomized_greater_than_screened():

    findings = [
        {
            "role": "SCREENED",
            "section": "results",
            "numeric_value": 45,
            "context": (
                "Of the 45 participants screened, "
                "52 participants were randomized into the study."
            )
        },
        {
            "role": "RANDOMIZED",
            "section": "results",
            "numeric_value": 52,
            "context": (
                "Of the 45 participants screened, "
                "52 participants were randomized into the study."
            )
        }
    ]

    result = detect_screening_to_randomization_flow(findings)

    assert result is not None

    assert result["screened"] == 45
    assert result["randomized"] == 52
    assert result["difference"] == -7

    assert result["interpretation"] == "POTENTIAL_DISCREPANCY"
