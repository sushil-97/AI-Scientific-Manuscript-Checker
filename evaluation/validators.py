
def validate_randomized_evidence(
    comparisons,
    expected_sections,
    expected_result
):
    if not expected_sections:
        return False

    return any(
        comparison.get("role") == "RANDOMIZED"
        and all(
            comparison["sections"].get(section) == counts
            for section, counts in expected_sections.items()
        )
        and comparison["result"] == expected_result
        for comparison in comparisons
    )
