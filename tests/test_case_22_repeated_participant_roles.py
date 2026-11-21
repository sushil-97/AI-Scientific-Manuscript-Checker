
from manuscript_checker import classify_sample_size_role


def test_repeated_participant_counts_have_different_roles():
    context = (
        "Of the 60 participants screened, "
        "60 participants were randomized into the study."
    )

    first_start = context.find("60 participants")

    second_start = context.find(
        "60 participants",
        first_start + 1
    )

    first_role = classify_sample_size_role(
        context,
        "60 participants",
        match_start=first_start
    )

    second_role = classify_sample_size_role(
        context,
        "60 participants",
        match_start=second_start
    )

    assert first_role == "SCREENED"
    assert second_role == "RANDOMIZED"
