from manuscript_checker import analyze_manuscript_text


def test_import():

    assert callable(
        analyze_manuscript_text
    )
