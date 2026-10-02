import pytest
from unittest.mock import MagicMock
from app.repositories.question_repository import QuestionRepository
from app.schemas.question_schema import QuestionCreate
from pymongo.errors import DuplicateKeyError

def test_create_question_success():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.questions = mock_collection

    repo = QuestionRepository(mock_db)

    q_data = QuestionCreate(
        question_id="JEE_MAIN_2026_APRIL_SHIFT_2_Q01",
        paper_id="JEE_MAIN_2026_APRIL_SHIFT_2",
        question_number=1,
        content="A uniform solid sphere of mass M...",
        options=[{"id": "A", "content": "7/5 MR^2"}],
        correct_option="A",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Parallel Axis Theorem",
        difficulty="Medium",
        question_type="MCQ",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 2"
    )

    created = repo.create_question(q_data)

    assert created.question_id == "JEE_MAIN_2026_APRIL_SHIFT_2_Q01"
    assert created.subject == "Physics"
    mock_collection.insert_one.assert_called_once()

def test_get_questions_by_ids_preserves_order():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.questions = mock_collection

    doc1 = {
        "question_id": "Q1",
        "paper_id": "P1",
        "question_number": 1,
        "content": "Q1 text",
        "year": 2026,
        "session": "April",
        "date": "2026-04-04",
        "shift": "Shift 1"
    }
    doc2 = {
        "question_id": "Q2",
        "paper_id": "P1",
        "question_number": 2,
        "content": "Q2 text",
        "year": 2026,
        "session": "April",
        "date": "2026-04-04",
        "shift": "Shift 1"
    }

    mock_collection.find.return_value = [doc2, doc1]  # Returned out of order by Mongo

    repo = QuestionRepository(mock_db)
    res = repo.get_questions_by_ids(["Q1", "Q2"])

    assert len(res) == 2
    assert res[0].question_id == "Q1"  # Preserved requested order
    assert res[1].question_id == "Q2"

def test_update_question_metadata():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.questions = mock_collection

    mock_collection.find_one_and_update.return_value = {
        "question_id": "Q1",
        "paper_id": "P1",
        "question_number": 1,
        "content": "Q1 text",
        "subject": "Physics",
        "chapter": "Rotational Motion",
        "year": 2026,
        "session": "April",
        "date": "2026-04-04",
        "shift": "Shift 1"
    }

    repo = QuestionRepository(mock_db)
    updated = repo.update_question_metadata("Q1", {"subject": "Physics", "chapter": "Rotational Motion"})

    assert updated is not None
    assert updated.subject == "Physics"
    assert updated.chapter == "Rotational Motion"
