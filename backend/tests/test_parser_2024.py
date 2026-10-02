"""
Unit and integration tests for the isolated 2024 JEE Main paper parsing workflow
and unified dispatcher layer.
"""

import os
import sys
# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from app.parsers import parse_paper, UnsupportedPaperFormatError
from app.parsers.y2024.answer_key_parser import parse_2024_answer_key, detect_answer_key_page
from app.parsers.y2024.question_parser import extract_mcq_options, get_subject_for_qnum, is_expected_mcq_2024
from app.parsers.y2024.validator import validate_2024_paper
from app.parsers.y2024.parser import parse_2024_paper, parse_metadata_from_filename
from app.parsers.dispatcher import detect_year_from_input
from app.services.embedding_service import EmbeddingService
from app.schemas.question_schema import QuestionCreate

SAMPLE_ANSWER_KEY_2024_TEXT = """
2024 (01 Feb Shift 1)                                       JEE Main Previous Year Paper
JEE Main 2024 January                                                                   MathonGo

                                               ANSWER KEYS
Physics
1.   (2)          2.   (4)          3.   (1)          4.   (3)          5.   (2)
6.   (2)          7.   (2)          8.   (2)          9.   (1)          10.  (1)
11.  (1)          12.  (3)          13.  (3)          14.  (4)          15.  (3)
16.  (2)          17.  (4)          18.  (4)          19.  (1)          20.  (4)
21.  (52)         22.  (3)          23.  (9600)       24.  (6)          25.  (3)
26.  (22)         27.  (72)         28.  (216)        29.  (15)         30.  (27)
Chemistry
31.  (1)          32.  (4)          33.  (3)          34.  (4)          35.  (4)
"""

def test_parse_2024_answer_key_mcq_and_numerical():
    """Test regex parsing of 2024 answer keys for MCQ and Numerical entries."""
    ans_map = parse_2024_answer_key(SAMPLE_ANSWER_KEY_2024_TEXT)
    
    assert 1 in ans_map
    assert ans_map[1]["raw"] == "2"

    assert 2 in ans_map
    assert ans_map[2]["raw"] == "4"

    assert 21 in ans_map
    assert ans_map[21]["raw"] == "52"

    assert 23 in ans_map
    assert ans_map[23]["raw"] == "9600"

    assert 31 in ans_map
    assert ans_map[31]["raw"] == "1"

def test_parse_2024_answer_key_decimals_and_multiline():
    """Test parsing decimal answers and multiline irregular spacing."""
    custom_text = """
    ANSWER KEYS
    51. (17.5)    52. (0.82)
    53.   (  240  )
    """
    ans_map = parse_2024_answer_key(custom_text)
    assert ans_map[51]["raw"] == "17.5"
    assert ans_map[52]["raw"] == "0.82"
    assert ans_map[53]["raw"] == "240"

def test_extract_mcq_options_standard():
    """Test option extraction from raw question text."""
    raw = """
    A particle of mass m moves in a horizontal plane. Find its velocity.
    (1) 12 m/s
    (2) 24 m/s
    (3) 36 m/s
    (4) 48 m/s
    """
    body, options = extract_mcq_options(raw)
    assert "A particle of mass m moves" in body
    assert len(options) == 4
    assert options[0]["id"] == "A"
    assert options[0]["content"] == "12 m/s"
    assert options[1]["id"] == "B"
    assert options[1]["content"] == "24 m/s"
    assert options[2]["id"] == "C"
    assert options[2]["content"] == "36 m/s"
    assert options[3]["id"] == "D"
    assert options[3]["content"] == "48 m/s"

def test_extract_mcq_options_statement_avoidance():
    """Test that statement (1) and (2) in question body don't break option extraction."""
    raw = """
    Given below are two statements:
    Statement (1) : The energy of electron is quantized.
    Statement (2) : Angular momentum is quantized.
    In the light of the above statements, choose the most appropriate answer:
    (1) Both Statement (1) and Statement (2) are correct.
    (2) Both Statement (1) and Statement (2) are incorrect.
    (3) Statement (1) is correct but Statement (2) is incorrect.
    (4) Statement (1) is incorrect but Statement (2) is correct.
    """
    body, options = extract_mcq_options(raw)
    assert "Given below are two statements" in body
    assert len(options) == 4
    assert options[0]["content"] == "Both Statement (1) and Statement (2) are correct."
    assert options[1]["content"] == "Both Statement (1) and Statement (2) are incorrect."
    assert options[2]["content"] == "Statement (1) is correct but Statement (2) is incorrect."
    assert options[3]["content"] == "Statement (1) is incorrect but Statement (2) is correct."

def test_extract_mcq_options_attached_digit():
    """Test option extraction when no whitespace precedes option marker, e.g. at x = 1(4)."""
    raw = """
    Find the derivative of g at x = 1.
    (1) continuous but not differentiable at x = 1
    (2) not continuous for all x
    (3) neither continuous nor differentiable at x = 1(4) continuous and differentiable
    """
    body, options = extract_mcq_options(raw)
    assert len(options) == 4
    assert options[2]["id"] == "C"
    assert options[3]["id"] == "D"
    assert options[3]["content"] == "continuous and differentiable"

def test_2024_subject_mapping():
    """Test deterministic 2024 JEE subject division by question number."""
    # Physics: 1-30
    assert get_subject_for_qnum(1) == "Physics"
    assert get_subject_for_qnum(30) == "Physics"
    # Chemistry: 31-60
    assert get_subject_for_qnum(31) == "Chemistry"
    assert get_subject_for_qnum(60) == "Chemistry"
    # Mathematics: 61-90
    assert get_subject_for_qnum(61) == "Mathematics"
    assert get_subject_for_qnum(90) == "Mathematics"

def test_2024_question_type_expected():
    """Test expected question type pattern for 2024."""
    # Physics MCQs (1-20), Numericals (21-30)
    assert is_expected_mcq_2024(1) is True
    assert is_expected_mcq_2024(20) is True
    assert is_expected_mcq_2024(21) is False
    assert is_expected_mcq_2024(30) is False
    # Chemistry MCQs (31-50), Numericals (51-60)
    assert is_expected_mcq_2024(31) is True
    assert is_expected_mcq_2024(50) is True
    assert is_expected_mcq_2024(51) is False
    assert is_expected_mcq_2024(60) is False
    # Mathematics MCQs (61-80), Numericals (81-90)
    assert is_expected_mcq_2024(61) is True
    assert is_expected_mcq_2024(80) is True
    assert is_expected_mcq_2024(81) is False
    assert is_expected_mcq_2024(90) is False

def test_validator_report_90_questions_success():
    """Test validator passes when all 90 questions and answers match."""
    fake_questions = [
        {
            "question_number": i,
            "question_type": "MCQ" if is_expected_mcq_2024(i) else "NUMERICAL",
            "options": [{"id": "A", "content": "1"}] * 4 if is_expected_mcq_2024(i) else [],
            "content": "Sample valid statement here"
        }
        for i in range(1, 91)
    ]
    fake_answers = {i: {"raw": "1"} for i in range(1, 91)}

    report = validate_2024_paper(fake_questions, fake_answers, expected_total=90)
    assert report["is_valid"] is True
    assert report["matched"] == 90
    assert len(report["missing_questions"]) == 0
    assert len(report["missing_answers"]) == 0
    assert len(report["anomalies"]) == 0

def test_validator_report_detects_missing_and_duplicates():
    """Test validator flags missing questions and duplicate entries."""
    fake_questions = [{"question_number": i, "content": "text"} for i in range(1, 89)]
    fake_questions.append({"question_number": 5, "content": "dup text"})
    fake_answers = {i: {"raw": "1"} for i in range(1, 85)}

    report = validate_2024_paper(fake_questions, fake_answers, expected_total=90)
    assert report["is_valid"] is False
    assert 5 in report["duplicate_questions"]
    assert 90 in report["missing_answers"]
    assert len(report["anomalies"]) > 0

def test_metadata_parsing_from_filename_2024():
    """Test parsing date, shift, and paper_id from standard 2024 filenames."""
    filename1 = "JEE Main 2024 (01 Feb Shift 1) Previous Year Paper with Answer Keys - MathonGo.pdf"
    meta1 = parse_metadata_from_filename(filename1)
    assert meta1["year"] == 2024
    assert meta1["date"] == "2024-02-01"
    assert meta1["shift"] == "Shift 1"
    assert meta1["session"] == "January"
    assert meta1["paper_id"] == "JEE_MAIN_2024_02_01_SHIFT_1"

    filename2 = "JEE Main 2024 (27 Jan Shift 2) Previous Year Paper with Answer Keys - MathonGo.pdf"
    meta2 = parse_metadata_from_filename(filename2)
    assert meta2["year"] == 2024
    assert meta2["date"] == "2024-01-27"
    assert meta2["shift"] == "Shift 2"
    assert meta2["session"] == "January"
    assert meta2["paper_id"] == "JEE_MAIN_2024_01_27_SHIFT_2"

def test_dispatcher_dispatch_2024():
    """Test dispatcher routes 2024 papers properly."""
    assert detect_year_from_input("path/to/JEE Main 2024 (01 Feb Shift 1).pdf") == 2024
    assert detect_year_from_input("custom.pdf", {"year": 2024}) == 2024

def test_rag_embedding_integrity_2024():
    """Verify that EmbeddingService format strictly excludes answers/options."""
    formatted = EmbeddingService.format_question_for_embedding(
        content="What is the force acting on the particle?",
        subject="Physics",
        chapter="Laws of Motion",
        concept="Newton's Second Law"
    )
    assert "What is the force acting on the particle?" in formatted
    assert "Physics" in formatted
    assert "Laws of Motion" in formatted
    assert "Option" not in formatted
    assert "Answer" not in formatted

def test_end_to_end_parse_2024_sample_paper():
    """End-to-end integration test parsing a real 2024 paper from disk."""
    pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "raw", "2024",
        "JEE Main 2024 (01 Feb Shift 1) Previous Year Paper with Answer Keys - MathonGo.pdf"
    )
    if not os.path.exists(pdf_path):
        pytest.skip("Test 2024 PDF not present in environment")

    questions, report = parse_paper(pdf_path, year=2024, return_report=True)

    assert len(questions) == 90
    assert report["matched"] == 90
    assert report["is_valid"] is True
    assert len(report["missing_questions"]) == 0
    assert len(report["missing_answers"]) == 0

    # Test Physics MCQ (Q1)
    q1 = questions[0]
    assert isinstance(q1, QuestionCreate)
    assert q1.question_number == 1
    assert q1.question_type == "MCQ"
    assert q1.subject == "Physics"
    assert q1.correct_option == "B"
    assert q1.answer["type"] == "MCQ"
    assert q1.answer["correct_option"] == "B"
    assert q1.metadata["source_format"] == "2024_separate_answer_key"
    assert len(q1.options) == 4

    # Test Physics Numerical (Q21)
    q21 = [q for q in questions if q.question_number == 21][0]
    assert isinstance(q21, QuestionCreate)
    assert q21.question_number == 21
    assert q21.question_type == "NUMERICAL"
    assert q21.subject == "Physics"
    assert q21.numerical_answer == 52.0
    assert q21.answer["type"] == "NUMERICAL"
    assert q21.answer["value"] == 52.0
    assert len(q21.options) == 0

    # Test Chemistry MCQ (Q31)
    q31 = [q for q in questions if q.question_number == 31][0]
    assert q31.subject == "Chemistry"
    assert q31.question_type == "MCQ"
    assert len(q31.options) == 4

    # Test Mathematics MCQ (Q61)
    q61 = [q for q in questions if q.question_number == 61][0]
    assert q61.subject == "Mathematics"
    assert q61.question_type == "MCQ"
    assert len(q61.options) == 4

    # Test Mathematics Numerical (Q90)
    q90 = [q for q in questions if q.question_number == 90][0]
    assert q90.subject == "Mathematics"
    assert q90.question_type == "NUMERICAL"
    assert len(q90.options) == 0

if __name__ == "__main__":
    test_parse_2024_answer_key_mcq_and_numerical()
    test_parse_2024_answer_key_decimals_and_multiline()
    test_extract_mcq_options_standard()
    test_extract_mcq_options_statement_avoidance()
    test_extract_mcq_options_attached_digit()
    test_2024_subject_mapping()
    test_2024_question_type_expected()
    test_validator_report_90_questions_success()
    test_validator_report_detects_missing_and_duplicates()
    test_metadata_parsing_from_filename_2024()
    test_dispatcher_dispatch_2024()
    test_rag_embedding_integrity_2024()
    test_end_to_end_parse_2024_sample_paper()
    print("ALL 2024 PARSER UNIT AND INTEGRATION TESTS PASSED!")
