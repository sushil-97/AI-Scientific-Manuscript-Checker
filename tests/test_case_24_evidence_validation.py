
from evaluation.run_evaluation import validate_randomized_evidence


def test_correct_randomized_evidence():
    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [150],
                "methods": [150],
                "results": [142]
            },
            "result": "POTENTIAL_DISCREPANCY"
        }
    ]

    expected_sections = {
        "abstract": [150],
        "methods": [150],
        "results": [142]
    }

    result = validate_randomized_evidence(
        comparisons,
        expected_sections,
        "POTENTIAL_DISCREPANCY"
    )

    assert result is True


def test_incorrect_randomized_evidence():
    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [150],
                "methods": [150],
                "results": [142]
            },
            "result": "POTENTIAL_DISCREPANCY"
        }
    ]

    expected_sections = {
        "abstract": [150],
        "methods": [150],
        "results": [145]
    }

    result = validate_randomized_evidence(
        comparisons,
        expected_sections,
        "POTENTIAL_DISCREPANCY"
    )

    assert result is False
