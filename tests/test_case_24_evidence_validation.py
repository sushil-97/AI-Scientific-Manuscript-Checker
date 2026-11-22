import pytest

from evaluation.validators import (
    validate_randomized_evidence,
    parse_strict_validation,
)

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


def test_missing_section_evidence():
    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [150],
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

    assert result is False


def test_incorrect_classification():
    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [150],
                "methods": [150],
                "results": [142]
            },
            "result": "CONSISTENT"
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

    assert result is False


def test_wrong_participant_role():
    comparisons = [
        {
            "role": "SCREENED",
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

    assert result is False


def test_empty_expected_evidence():
    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [120],
                "methods": [120],
                "results": [120]
            },
            "result": "CONSISTENT"
        }
    ]

    result = validate_randomized_evidence(
        comparisons,
        {},
        "CONSISTENT"
    )

    assert result is False


def test_unexpected_extra_participant_count():
    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [120],
                "methods": [120],
                "results": [120, 135]
            },
            "result": "CONSISTENT"
        }
    ]

    expected_sections = {
        "abstract": [120],
        "methods": [120],
        "results": [120]
    }

    result = validate_randomized_evidence(
        comparisons,
        expected_sections,
        "CONSISTENT"
    )

    assert result is False


def test_additional_unexpected_section_is_allowed():
    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [120],
                "methods": [120],
                "results": [135]
            },
            "result": "POTENTIAL_DISCREPANCY"
        }
    ]

    expected_sections = {
        "abstract": [120],
        "methods": [120]
    }

    result = validate_randomized_evidence(
        comparisons,
        expected_sections,
        "POTENTIAL_DISCREPANCY"
    )

    assert result is True



def test_strict_mode_rejects_extra_section():
    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [120],
                "methods": [120],
                "results": [135]
            },
            "result": "POTENTIAL_DISCREPANCY"
        }
    ]

    expected_sections = {
        "abstract": [120],
        "methods": [120]
    }

    result = validate_randomized_evidence(
        comparisons,
        expected_sections,
        "POTENTIAL_DISCREPANCY",
        strict=True
    )

    assert result is False


def test_strict_mode_accepts_exact_evidence():
    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [120],
                "methods": [120],
                "results": [120]
            },
            "result": "CONSISTENT"
        }
    ]

    expected_sections = {
        "abstract": [120],
        "methods": [120],
        "results": [120]
    }

    result = validate_randomized_evidence(
        comparisons,
        expected_sections,
        "CONSISTENT",
        strict=True
    )

    assert result is True


def test_csv_strict_mode_rejects_unexpected_section():
    # Simulate the strict_validation value from CSV
    csv_value = "True"
    strict_mode = csv_value.strip().lower() == "true"

    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [120],
                "methods": [120],
                "results": [120]
            },
            "result": "CONSISTENT"
        }
    ]

    # Expected evidence intentionally excludes Results
    expected_sections = {
        "abstract": [120],
        "methods": [120]
    }

    result = validate_randomized_evidence(
        comparisons,
        expected_sections,
        "CONSISTENT",
        strict=strict_mode
    )

    assert result is False


def test_csv_strict_mode_rejects_unexpected_section():
    # Simulate the strict_validation value from CSV
    csv_value = "True"
    strict_mode = csv_value.strip().lower() == "true"

    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [120],
                "methods": [120],
                "results": [120]
            },
            "result": "CONSISTENT"
        }
    ]

    # Expected evidence intentionally excludes Results
    expected_sections = {
        "abstract": [120],
        "methods": [120]
    }

    result = validate_randomized_evidence(
        comparisons,
        expected_sections,
        "CONSISTENT",
        strict=strict_mode
    )

    assert result is False


def test_csv_partial_mode_allows_extra_section():
    # Simulate the strict_validation value from CSV
    csv_value = "False"
    strict_mode = csv_value.strip().lower() == "true"

    comparisons = [
        {
            "role": "RANDOMIZED",
            "sections": {
                "abstract": [120],
                "methods": [120],
                "results": [120]
            },
            "result": "CONSISTENT"
        }
    ]

    # Expected evidence contains only two sections
    expected_sections = {
        "abstract": [120],
        "methods": [120]
    }

    result = validate_randomized_evidence(
        comparisons,
        expected_sections,
        "CONSISTENT",
        strict=strict_mode
    )

    assert result is True


def test_parse_strict_validation_true():
    result = parse_strict_validation("True")
    assert result is True


def test_parse_strict_validation_false():
    result = parse_strict_validation("False")
    assert result is False


def test_parse_strict_validation_invalid():
    with pytest.raises(ValueError):
        parse_strict_validation("maybe")




