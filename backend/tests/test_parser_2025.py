"""
Unit and integration tests for the isolated 2025 JEE Main paper parsing workflow
and the unified dispatcher layer.
"""

import os
import sys
# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from app.parsers import parse_paper, UnsupportedPaperFormatError
from app.parsers.y2025.answer_key_parser import parse_2025_answer_key, detect_answer_key_page
from app.parsers.y2025.question_parser import extract_mcq_options, get_subject_for_qnum
from app.parsers.y2025.validator import validate_2025_paper
from app.parsers.y2025.parser import parse_2025_paper, parse_metadata_from_filename
from app.parsers.dispatcher import detect_year_from_input
from app.services.embedding_service import EmbeddingService
from app.schemas.question_schema import QuestionCreate

SAMPLE_ANSWER_KEY_TEXT = """
2025 (22 Jan Shift 1)                                      JEE Main Previous Year Paper
JEE Main 2025 January                                                                   MathonGo

                                               ANSWER KEYS
Mathematics
1.   (4)          2.   (3)          3.   (1)          4.   (4)          5.   (2)
6.   (2)          7.   (1)          8.   (3)          9.   (4)          10.  (2)
11.  (3)          12.  (4)          13.  (1)          14.  (2)          15.  (4)
16.  (1)          17.  (3)          18.  (4)          19.  (2)          20.  (1)
21.  (34)         22.  (2035)       23.  (2)          24.  (27)         25.  (52)
Physics
26.  (2)          27.  (1)          28.  (4)          29.  (2)          30.  (3)
"""

def test_parse_2025_answer_key_mcq_and_numerical():
    """Test regex parsing of 2025 answer keys for MCQ and Numerical entries."""
    ans_map = parse_2025_answer_key(SAMPLE_ANSWER_KEY_TEXT)
    
    assert 1 in ans_map
    assert ans_map[1]["raw"] == "4"

    assert 2 in ans_map
    assert ans_map[2]["raw"] == "3"

    assert 21 in ans_map
    assert ans_map[21]["raw"] == "34"

    assert 22 in ans_map
    assert ans_map[22]["raw"] == "2035"

    assert 26 in ans_map
    assert ans_map[26]["raw"] == "2"

def test_parse_2025_answer_key_decimals_and_multiline():
    """Test parsing decimal answers and multiline irregular spacing."""
    custom_text = """
    ANSWER KEYS
    46. (2.5)    47. (0.75)
    48.   (  150  )
    """
    ans_map = parse_2025_answer_key(custom_text)
    assert ans_map[46]["raw"] == "2.5"
    assert ans_map[47]["raw"] == "0.75"
    assert ans_map[48]["raw"] == "150"

def test_extract_mcq_options_standard():
    """Test option extraction from raw question text."""
    raw = """
    Let a1, a2 be real numbers. Find the maximum value.
    (1) 628
    (2) 812
    (3) 526
    (4) 784
    """
    body, options = extract_mcq_options(raw)
    assert "Let a1, a2 be real numbers" in body
    assert len(options) == 4
    assert options[0]["id"] == "A"
    assert options[0]["content"] == "628"
    assert options[1]["id"] == "B"
    assert options[1]["content"] == "812"
    assert options[2]["id"] == "C"
    assert options[2]["content"] == "526"
    assert options[3]["id"] == "D"
    assert options[3]["content"] == "784"

def test_extract_mcq_options_statement_avoidance():
    """Test that statement (1) and (2) in question body and nested (1), (2) in options don't break option extraction."""
    raw = """
    Consider the following statements:
    (1) Statement one is true.
    (2) Statement two is false.
    Which of the above are correct?
    (1) Statement 1 only
    (2) Statement 2 only
    (3) Both (1) and (2)
    (4) Neither (1) nor (2)
    """
    body, options = extract_mcq_options(raw)
    assert "Consider the following statements" in body
    assert len(options) == 4
    assert options[0]["content"] == "Statement 1 only"
    assert options[1]["content"] == "Statement 2 only"
    assert options[2]["content"] == "Both (1) and (2)"
    assert options[3]["content"] == "Neither (1) nor (2)"

def test_subject_mapping():
    """Test deterministic JEE subject division by question number."""
    assert get_subject_for_qnum(1) == "Mathematics"
    assert get_subject_for_qnum(25) == "Mathematics"
    assert get_subject_for_qnum(26) == "Physics"
    assert get_subject_for_qnum(50) == "Physics"
    assert get_subject_for_qnum(51) == "Chemistry"
    assert get_subject_for_qnum(75) == "Chemistry"

def test_validator_report_success():
    """Test validator passes when questions and answers match perfectly."""
    fake_questions = [{"question_number": i, "question_type": "MCQ" if i <= 60 else "NUMERICAL", "options": [{"id": "A", "content": "1"}] * 4 if i <= 60 else [], "content": "Sample statement here"} for i in range(1, 76)]
    fake_answers = {i: {"raw": "1"} for i in range(1, 76)}

    report = validate_2025_paper(fake_questions, fake_answers, expected_total=75)
    assert report["is_valid"] is True
    assert report["matched"] == 75
    assert len(report["missing_questions"]) == 0
    assert len(report["missing_answers"]) == 0
    assert len(report["anomalies"]) == 0

def test_validator_report_detects_missing_and_duplicates():
    """Test validator flags missing questions and duplicate entries."""
    # Questions missing 10 and 20, duplicate 5
    fake_questions = [{"question_number": i, "content": "text"} for i in range(1, 74)]
    fake_questions.append({"question_number": 5, "content": "dup text"})
    fake_answers = {i: {"raw": "1"} for i in range(1, 70)} # answers missing 70..75

    report = validate_2025_paper(fake_questions, fake_answers, expected_total=75)
    assert report["is_valid"] is False
    assert 5 in report["duplicate_questions"]
    assert 75 in report["missing_answers"]
    assert len(report["anomalies"]) > 0

def test_metadata_parsing_from_filename():
    """Test parsing date, shift, and paper_id from standard 2025 filenames."""
    filename = "JEE Main 2025 (22 Jan Shift 1) Previous Year Paper with Answer Keys - MathonGo.pdf"
    meta = parse_metadata_from_filename(filename)
    assert meta["year"] == 2025
    assert meta["date"] == "2025-01-22"
    assert meta["shift"] == "Shift 1"
    assert meta["session"] == "January"
    assert meta["paper_id"] == "JEE_MAIN_2025_01_22_SHIFT_1"

def test_dispatcher_detect_year():
    """Test year inference in dispatcher."""
    assert detect_year_from_input("path/to/JEE Main 2025 (22 Jan Shift 1).pdf") == 2025
    assert detect_year_from_input("path/to/paper_2026_apr.pdf") == 2026
    assert detect_year_from_input("custom.pdf", {"year": 2025}) == 2025
    assert detect_year_from_input("custom.pdf", {"year": "2026"}) == 2026

def test_dispatcher_unsupported_year():
    """Test dispatcher raises UnsupportedPaperFormatError on unknown years."""
    # Create a dummy temporary file
    temp_file = "temp_unknown_paper.pdf"
    with open(temp_file, "w") as f:
        f.write("%PDF-1.4 dummy")
    try:
        with pytest.raises(UnsupportedPaperFormatError):
            parse_paper(temp_file, year=2020)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_rag_embedding_integrity():
    """Verify that EmbeddingService format NEVER includes answers or correct options."""
    formatted = EmbeddingService.format_question_for_embedding(
        content="What is the acceleration due to gravity?",
        subject="Physics",
        chapter="Gravitation",
        concept="Free Fall"
    )
    assert "What is the acceleration due to gravity?" in formatted
    assert "Physics" in formatted
    assert "Gravitation" in formatted
    # Crucial: verify that answers and options are never included
    assert "Option" not in formatted
    assert "Answer" not in formatted

def test_end_to_end_parse_2025_shift1():
    """End-to-end integration test parsing a real 2025 paper from disk."""
    pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "raw", "2025",
        "JEE Main 2025 (22 Jan Shift 1) Previous Year Paper with Answer Keys - MathonGo.pdf"
    )
    if not os.path.exists(pdf_path):
        pytest.skip("Test 2025 PDF not present in environment")

    questions, report = parse_paper(pdf_path, year=2025, return_report=True)

    assert len(questions) == 75
    assert report["matched"] == 75
    assert report["is_valid"] is True
    assert len(report["missing_questions"]) == 0
    assert len(report["missing_answers"]) == 0

    # Test MCQ question schema conformity
    q1 = questions[0]
    assert isinstance(q1, QuestionCreate)
    assert q1.question_number == 1
    assert q1.question_type == "MCQ"
    assert q1.subject == "Mathematics"
    assert q1.correct_option == "D"
    assert q1.answer["type"] == "MCQ"
    assert q1.answer["correct_option"] == "D"
    assert q1.metadata["source_format"] == "2025_separate_answer_key"
    assert len(q1.options) == 4

    # Test Numerical question schema conformity
    q21 = [q for q in questions if q.question_number == 21][0]
    assert isinstance(q21, QuestionCreate)
    assert q21.question_number == 21
    assert q21.question_type == "NUMERICAL"
    assert q21.subject == "Mathematics"
    assert q21.numerical_answer == 34.0
    assert q21.answer["type"] == "NUMERICAL"
    assert q21.answer["value"] == 34.0
    assert len(q21.options) == 0

if __name__ == "__main__":
    test_parse_2025_answer_key_mcq_and_numerical()
    test_parse_2025_answer_key_decimals_and_multiline()
    test_extract_mcq_options_standard()
    test_extract_mcq_options_statement_avoidance()
    test_subject_mapping()
    test_validator_report_success()
    test_validator_report_detects_missing_and_duplicates()
    test_metadata_parsing_from_filename()
    test_dispatcher_detect_year()
    test_rag_embedding_integrity()
    test_end_to_end_parse_2025_shift1()
    print("ALL 2025 PARSER UNIT AND INTEGRATION TESTS PASSED!")
