from manuscript_checker import detect_screening_to_randomization_flow


def test_screening_to_randomization_flow():

    context = (
        "A total of 69 infants were assessed for eligibility "
        "and 52 infants underwent randomization."
    )

    findings = [
        {
            "role": "SCREENED",
            "section": "results",
            "numeric_value": 69,
            "context": context
        },
        {
            "role": "RANDOMIZED",
            "section": "results",
            "numeric_value": 52,
            "context": context
        }
    ]

    result = detect_screening_to_randomization_flow(findings)

    assert result is not None
    assert result["screened"] == 69
    assert result["randomized"] == 52
    assert result["difference"] == 17

    assert result["interpretation"] == "INFORMATIONAL_ONLY"

    assert result["evidence"]["section"] == "results"
    assert "69 infants" in result["evidence"]["text"]
    assert "52 infants" in result["evidence"]["text"]
