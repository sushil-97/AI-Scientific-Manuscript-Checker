from manuscript_checker import (
    extract_sample_sizes,
    classify_sample_size_role,
)


def test_randomization_and_allocation_roles():
    sentence = (
        "A total of 69 infants were assessed for eligibility "
        "between April 1, 2022 and December 31, 2023, "
        "and 52 infants underwent randomization with "
        "26 participants allocated to each of the "
        "Early and Late fortification arms."
    )

    findings = extract_sample_sizes({
        "results": sentence
    })

    roles = {
        (finding["numeric_value"],
         classify_sample_size_role(
             finding["context"],
             finding["expression"]
         ))
        for finding in findings
    }

    assert (69, "SCREENED") in roles
    assert (52, "RANDOMIZED") in roles
    assert (26, "ALLOCATED") in roles
