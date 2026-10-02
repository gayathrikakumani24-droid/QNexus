import pytest
from unittest.mock import MagicMock
from app.services.mistake_service import MistakeService
from app.repositories.mistake_repository import MistakeRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.question_schema import QuestionResponse
from app.schemas.mistake_schema import MistakeCreateRequest, MistakeUpdateRequest, MistakeResponse

def test_create_mistake_auto_populates_question_metadata():
    mock_mistake_repo = MagicMock(spec=MistakeRepository)
    mock_question_repo = MagicMock(spec=QuestionRepository)

    mock_q = QuestionResponse(
        question_id="JEE_MAIN_2026_01_24_S1_Q_01",
        paper_id="JEE_MAIN_2026_01_24_S1",
        question_number=1,
        content="Find the moment of inertia.",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Moment of Inertia",
        difficulty="Medium",
        correct_option="B",
        year=2026,
        session="January",
        date="2026-01-24",
        shift="Shift 1"
    )
    mock_question_repo.get_question.return_value = mock_q

    mock_mistake_repo.create_or_update_mistake.return_value = {
        "_id": "MST_123456",
        "mistake_id": "MST_123456",
        "user_id": "default_user",
        "question_id": "JEE_MAIN_2026_01_24_S1_Q_01",
        "subject": "Physics",
        "chapter": "Rotational Motion",
        "concept": "Moment of Inertia",
        "user_answer": "A",
        "correct_answer": "B",
        "mistake_tag": "Calculation Error",
        "user_notes": "Forgot factor of 1/2 for solid disc",
        "review_status": "Needs Review"
    }

    service = MistakeService(
        mistake_repo=mock_mistake_repo,
        question_repo=mock_question_repo
    )

    req = MistakeCreateRequest(
        question_id="JEE_MAIN_2026_01_24_S1_Q_01",
        user_answer="A",
        mistake_tag="Calculation Error",
        user_notes="Forgot factor of 1/2 for solid disc"
    )

    res = service.create_mistake(req)

    assert isinstance(res, MistakeResponse)
    assert res.mistake_id == "MST_123456"
    assert res.subject == "Physics"
    assert res.chapter == "Rotational Motion"
    assert res.correct_answer == "B"
    assert res.mistake_tag == "Calculation Error"
    assert res.question.content == "Find the moment of inertia."

def test_list_mistakes_hydrates_questions():
    mock_mistake_repo = MagicMock(spec=MistakeRepository)
    mock_question_repo = MagicMock(spec=QuestionRepository)

    mock_mistake_repo.list_mistakes.return_value = [
        {
            "_id": "MST_1",
            "mistake_id": "MST_1",
            "user_id": "default_user",
            "question_id": "Q_1",
            "subject": "Chemistry",
            "chapter": "Thermodynamics",
            "concept": "Enthalpy",
            "user_answer": "C",
            "correct_answer": "D",
            "mistake_tag": "Formula Forgotten",
            "user_notes": "Review Hess law formula",
            "review_status": "Needs Review"
        }
    ]
    mock_mistake_repo.count_mistakes.return_value = 1

    mock_q = QuestionResponse(
        question_id="Q_1",
        paper_id="PAPER_1",
        question_number=1,
        content="Calculate delta H.",
        subject="Chemistry",
        chapter="Thermodynamics",
        concept="Enthalpy",
        year=2026,
        session="January",
        date="2026-01-24",
        shift="Shift 1"
    )
    mock_question_repo.get_questions_by_ids.return_value = [mock_q]

    service = MistakeService(
        mistake_repo=mock_mistake_repo,
        question_repo=mock_question_repo
    )

    res = service.list_mistakes()

    assert res.total == 1
    assert len(res.mistakes) == 1
    assert res.mistakes[0].mistake_id == "MST_1"
    assert res.mistakes[0].question.content == "Calculate delta H."

def test_update_and_delete_mistake():
    mock_mistake_repo = MagicMock(spec=MistakeRepository)
    mock_question_repo = MagicMock(spec=QuestionRepository)

    mock_mistake_repo.update_mistake.return_value = {
        "mistake_id": "MST_1",
        "user_id": "default_user",
        "question_id": "Q_1",
        "subject": "Physics",
        "chapter": "Optics",
        "concept": "Refraction",
        "mistake_tag": "Silly Mistake",
        "user_notes": "Updated note",
        "review_status": "Mastered"
    }
    mock_mistake_repo.delete_mistake.return_value = True
    mock_question_repo.get_question.return_value = None

    service = MistakeService(
        mistake_repo=mock_mistake_repo,
        question_repo=mock_question_repo
    )

    update_res = service.update_mistake(
        "MST_1",
        MistakeUpdateRequest(review_status="Mastered", user_notes="Updated note")
    )
    assert update_res.review_status == "Mastered"
    assert update_res.user_notes == "Updated note"

    del_res = service.delete_mistake("MST_1")
    assert del_res is True
