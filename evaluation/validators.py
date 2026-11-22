
def validate_randomized_evidence(
    comparisons,
    expected_sections,
    expected_result,
    strict=False
):
    if not expected_sections:
        return False

    return any(
        comparison.get("role") == "RANDOMIZED"
        and all(
            comparison["sections"].get(section) == counts
            for section, counts in expected_sections.items()
        )
        and (
            not strict
            or set(comparison["sections"]) == set(expected_sections)
        )
        and comparison["result"] == expected_result
        for comparison in comparisons
    )
