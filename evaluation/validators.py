def validate_randomized_evidence(
    comparisons,
    expected_sections,
    expected_result
):
    return any(
        all(
            comparison["sections"].get(section) == counts
            for section, counts in expected_sections.items()
        )
        and comparison["result"] == expected_result
        for comparison in comparisons
    )
