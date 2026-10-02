import pytest
from unittest.mock import MagicMock
from app.services.practice_service import PracticeService
from app.schemas.practice_schema import PracticeStartRequest, PracticeAnswerRequest
from app.schemas.question_schema import QuestionResponse

def test_start_session_success():
    mock_db = MagicMock()
    mock_question_repo = MagicMock()
    mock_practice_repo = MagicMock()

    q1 = QuestionResponse(
        question_id="Q1",
        paper_id="P1",
        question_number=1,
        content="Q1 Content",
        options=[{"id": "A", "content": "Opt A"}],
        subject="Physics",
        chapter="Rotational Motion",
        difficulty="Medium",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    mock_question_repo.list_questions.return_value = [q1]
    mock_practice_repo.create_session.return_value = "SESS_TEST_123"

    service = PracticeService(
        db=mock_db,
        question_repo=mock_question_repo,
        practice_repo=mock_practice_repo
    )

    req = PracticeStartRequest(subject="Physics", num_questions=1)
    res = service.start_session(req)

    assert res.session_id == "SESS_TEST_123"
    assert res.total_questions == 1
    assert res.questions[0].question_id == "Q1"
    assert res.status == "IN_PROGRESS"

def test_submit_session_scoring():
    mock_db = MagicMock()
    mock_question_repo = MagicMock()
    mock_practice_repo = MagicMock()

    q1 = QuestionResponse(
        question_id="Q1",
        paper_id="P1",
        question_number=1,
        content="Q1 Content",
        options=[{"id": "A", "content": "Opt A"}, {"id": "B", "content": "Opt B"}],
        correct_option="A",
        question_type="MCQ",
        subject="Physics",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    q2 = QuestionResponse(
        question_id="Q2",
        paper_id="P1",
        question_number=2,
        content="Q2 Content",
        options=[{"id": "A", "content": "Opt A"}, {"id": "B", "content": "Opt B"}],
        correct_option="B",
        question_type="MCQ",
        subject="Physics",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    q3 = QuestionResponse(
        question_id="Q3",
        paper_id="P1",
        question_number=3,
        content="Q3 Content",
        options=[{"id": "A", "content": "Opt A"}],
        correct_option="A",
        question_type="MCQ",
        subject="Physics",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    mock_practice_repo.get_session.return_value = {
        "session_id": "SESS_TEST_123",
        "question_ids": ["Q1", "Q2", "Q3"],
        "answers": {
            "Q1": {"selected_answer": "A", "time_spent_seconds": 60, "marked_for_review": False},  # Correct (+4)
            "Q2": {"selected_answer": "A", "time_spent_seconds": 45, "marked_for_review": False},  # Incorrect (-1)
            # Q3 is Unattempted (0)
        }
    }

    mock_question_repo.get_questions_by_ids.return_value = [q1, q2, q3]

    service = PracticeService(
        db=mock_db,
        question_repo=mock_question_repo,
        practice_repo=mock_practice_repo
    )

    submit_res = service.submit_session("SESS_TEST_123")

    assert submit_res.session_id == "SESS_TEST_123"
    assert submit_res.total_questions == 3
    assert submit_res.correct_count == 1
    assert submit_res.incorrect_count == 1
    assert submit_res.unattempted_count == 1
    assert submit_res.score == 3  # (+4 - 1 + 0 = 3)
    assert submit_res.accuracy_percentage == 50.0

    mock_practice_repo.record_attempts_bulk.assert_called_once()
    mock_practice_repo.complete_session.assert_called_once()
