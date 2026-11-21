
from manuscript_checker import normalize_written_sample_numbers


def test_fifty_participants():
    text = "Fifty participants were randomized."

    result = normalize_written_sample_numbers(text)

    assert result == "50 participants were randomized."


def test_sixty_participants():
    text = "Sixty participants were screened."

    result = normalize_written_sample_numbers(text)

    assert result == "60 participants were screened."


def test_numeric_participants_unchanged():
    text = "50 participants were randomized."

    result = normalize_written_sample_numbers(text)

    assert result == text


def test_unrelated_words_unchanged():
    text = "Fifty patients were enrolled."

    result = normalize_written_sample_numbers(text)

    assert result == text
