import os
import pytest
from app.services.pdf_parser import extract_pages_from_pdf
from app.services.extractor_service import extract_questions_from_pages, parse_options_from_text

RAW_PDF_SAMPLE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "raw", "JEE Main 2026 05 April Morning Shift Questions.pdf"
)

def test_parse_options_from_text():
    sample_text = (
        "Consider the system of linear equations:\n"
        "(1) is a constant function\n"
        "(2) is strictly increasing\n"
        "(3) is strictly decreasing\n"
        "(4) has two critical points\n"
    )
    content, options = parse_options_from_text(sample_text)
    assert len(options) == 4
    assert options[0].id == "A"
    assert "constant function" in options[0].content
    assert options[1].id == "B"
    assert options[3].id == "D"

def test_extract_questions_from_pages_mock():
    mock_pages = [
        {
            "page_number": 1,
            "text": "Q1. Find value of x if x + 2 = 5.\n(1) 1\n(2) 2\n(3) 3\n(4) 4\n\nQ2. Solve integral of x dx.\n"
        },
        {
            "page_number": 2,
            "text": "Q3. Which gas is noble?\n(A) Helium\n(B) Nitrogen\n(C) Oxygen\n(D) Chlorine\n"
        }
    ]

    paper_meta = {
        "year": 2026,
        "session": "April",
        "date": "2026-04-05",
        "shift": "Shift 1",
        "exam": "JEE Main"
    }

    questions = extract_questions_from_pages(mock_pages, "TEST_PAPER_01", paper_meta)

    assert len(questions) == 3
    assert questions[0].question_number == 1
    assert questions[0].question_id == "JEE_MAIN_2026_04_05_SHIFT_1_Q_1"
    assert questions[0].page_number == 1
    assert len(questions[0].options) == 4

    assert questions[1].question_number == 2
    assert questions[1].question_type == "NUMERICAL"

    assert questions[2].question_number == 3
    assert questions[2].page_number == 2
    assert len(questions[2].options) == 4

def test_extract_pages_from_real_jee_pdf_if_available():
    if os.path.exists(RAW_PDF_SAMPLE):
        pages_data, warnings = extract_pages_from_pdf(
            RAW_PDF_SAMPLE,
            "JEE_MAIN_2026_APRIL_05_S1",
            output_dir=os.path.join(os.path.dirname(RAW_PDF_SAMPLE), "..", "processed")
        )
        assert len(pages_data) > 0
        assert pages_data[0]["page_number"] == 1

        questions = extract_questions_from_pages(
            pages_data,
            "JEE_MAIN_2026_APRIL_05_S1",
            {"year": 2026, "session": "April", "date": "2026-04-05", "shift": "Morning Shift"}
        )
        assert len(questions) >= 50
        assert questions[0].question_id.startswith("JEE_MAIN_2026_")
