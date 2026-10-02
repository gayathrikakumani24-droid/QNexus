import pytest
from unittest.mock import MagicMock
from app.schemas.question_metadata import QuestionMetadata, ClassificationSummaryResponse
from app.services.metadata_service import MetadataClassificationService
from app.schemas.question_schema import QuestionResponse

def test_question_metadata_validation():
    # Valid input
    meta = QuestionMetadata(
        subject="Physics",
        chapter="Rotational Motion",
        concept="Torque",
        difficulty="Medium",
        question_type="MCQ"
    )
    assert meta.subject == "Physics"
    assert meta.difficulty == "Medium"
    assert meta.question_type == "MCQ"

    # Messy casing and normalization
    meta2 = QuestionMetadata(
        subject="physics",
        chapter="Calculus",
        concept="Integration",
        difficulty="hard",
        question_type="numerical"
    )
    assert meta2.subject == "Physics"
    assert meta2.difficulty == "Hard"
    assert meta2.question_type == "Numerical"

    # Unknown fallback
    meta3 = QuestionMetadata(
        subject="Biology",
        chapter="Genetics",
        concept="DNA",
        difficulty="Extreme",
        question_type="Essay"
    )
    assert meta3.subject == "Unknown"
    assert meta3.difficulty == "Unknown"
    assert meta3.question_type == "Unknown"

def test_classify_question_with_mocked_llm():
    mock_db = MagicMock()
    mock_llm = MagicMock()
    
    mock_llm.generate_json_completion.return_value = {
        "subject": "Physics",
        "chapter": "Rotational Motion",
        "concept": "Parallel Axis Theorem",
        "difficulty": "Medium",
        "question_type": "MCQ"
    }

    service = MetadataClassificationService(db=mock_db, llm_client=mock_llm)
    result = service.classify_question(
        "A uniform solid sphere...",
        [{"id": "A", "content": "7/5 MR^2"}]
    )

    assert result.subject == "Physics"
    assert result.chapter == "Rotational Motion"
    assert result.concept == "Parallel Axis Theorem"
    assert result.difficulty == "Medium"
    assert result.question_type == "MCQ"

def test_classify_paper_questions_batching_and_caching():
    mock_db = MagicMock()
    mock_llm = MagicMock()
    mock_cursor = MagicMock()
    
    # Question 1 is already classified
    q1 = QuestionResponse(
        question_id="Q1",
        paper_id="P1",
        question_number=1,
        content="Q1 text",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Torque",
        difficulty="Easy",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    # Question 2 is unclassified
    q2 = QuestionResponse(
        question_id="Q2",
        paper_id="P1",
        question_number=2,
        content="Q2 text",
        subject=None,
        chapter=None,
        concept=None,
        difficulty=None,
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = [q1.model_dump(by_alias=True), q2.model_dump(by_alias=True)]
    mock_db.questions.find.return_value = mock_cursor
    mock_db.questions.find_one_and_update.return_value = q2.model_dump(by_alias=True)

    mock_llm.generate_json_completion.return_value = {
        "subject": "Chemistry",
        "chapter": "Thermodynamics",
        "concept": "Enthalpy",
        "difficulty": "Hard",
        "question_type": "Numerical"
    }

    service = MetadataClassificationService(db=mock_db, llm_client=mock_llm)
    summary = service.classify_paper_questions(paper_id="P1", batch_size=2, overwrite=False)

    assert summary.paper_id == "P1"
    assert summary.processed == 2
    assert summary.successful == 2
    # Only Q2 should trigger LLM call because Q1 was already classified (cached)
    mock_llm.generate_json_completion.assert_called_once()
