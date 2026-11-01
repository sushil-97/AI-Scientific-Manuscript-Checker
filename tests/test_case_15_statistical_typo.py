from manuscript_checker import (
    detect_significance_claims,
    evaluate_claim_against_pvalue
)


def test_statistical_typo_does_not_create_false_discrepancy():

    sentence = (
        "There was no statically significant difference "
        "between groups (p = 0.9348)."
    )

    claims = detect_significance_claims(sentence)

    assert len(claims) == 1

    assert claims[0]["claim"] == "NOT_SIGNIFICANT"

    result = evaluate_claim_against_pvalue(
        claims[0]["claim"],
        0.9348
    )

    assert result == "CONSISTENT"
