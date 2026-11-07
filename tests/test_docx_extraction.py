from docx import Document
from manuscript_checker import analyze_manuscript


def test_docx_manuscript_analysis(tmp_path):

    # Create a temporary Word manuscript
    docx_path = tmp_path / "test_manuscript.docx"

    document = Document()

    document.add_paragraph("Title")
    document.add_paragraph("Synthetic Randomized Clinical Trial")

    document.add_paragraph("Abstract")
    document.add_paragraph("A total of 120 patients were randomized.")

    document.add_paragraph("Methods")
    document.add_paragraph(
        "This randomized clinical trial included human participants."
    )

    document.add_paragraph("Results")
    document.add_paragraph("A total of 120 patients were randomized.")

    document.add_paragraph("Discussion")
    document.add_paragraph("The findings were consistent.")

    document.add_paragraph("Data Availability")
    document.add_paragraph("Data are available upon reasonable request.")

    document.save(docx_path)

    # Run the actual manuscript analysis pipeline
    result = analyze_manuscript(str(docx_path))

    comparisons = result[
        "sample_size_screening"
    ]["same_role_comparisons"]

    # Verify that consistent counts are recognized
    assert any(
        comparison["role"] == "RANDOMIZED"
        and comparison["result"] == "CONSISTENT"
        and comparison["sections"].get("abstract") == [120]
        and comparison["sections"].get("results") == [120]
        for comparison in comparisons
    )
