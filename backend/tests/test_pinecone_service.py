import pytest
from unittest.mock import MagicMock
from app.repositories.vector_repository import VectorRepository
from app.services.pinecone_service import PineconeService
from app.schemas.question_schema import QuestionResponse

def test_question_id_to_point_id():
    q_id = "JEE_MAIN_2026_04_04_SHIFT_2_Q_1"
    res_id = VectorRepository.question_id_to_point_id(q_id)
    assert res_id == q_id

def test_sanitize_metadata_removes_none():
    payload = {
        "question_id": "Q1",
        "subject": "Physics",
        "numerical_answer": None,
        "year": 2026,
        "is_active": True,
        "tags": ["jee", "mechanics"],
        "unsupported_obj": {"nested": "value"}
    }
    sanitized = VectorRepository.sanitize_metadata(payload)
    
    assert "numerical_answer" not in sanitized
    assert sanitized["question_id"] == "Q1"
    assert sanitized["subject"] == "Physics"
    assert sanitized["year"] == 2026
    assert sanitized["is_active"] is True
    assert sanitized["tags"] == ["jee", "mechanics"]
    assert isinstance(sanitized["unsupported_obj"], str)

def test_vector_repository_upsert_records():
    mock_index = MagicMock()
    repo = VectorRepository(index=mock_index, index_name="test_index")

    records = [
        {
            "question_id": "Q1",
            "embedding": [0.1] * 384,
            "payload": {"subject": "Physics", "chapter": "Rotational Motion", "none_val": None}
        },
        {
            "question_id": "Q2",
            "embedding": [0.2] * 384,
            "payload": {"subject": "Chemistry", "chapter": "Thermodynamics"}
        }
    ]

    count = repo.upsert_records(records)
    assert count == 2
    mock_index.upsert.assert_called_once()
    call_args = mock_index.upsert.call_args[1]
    vectors = call_args["vectors"]
    assert len(vectors) == 2
    assert vectors[0]["id"] == "Q1"
    assert "none_val" not in vectors[0]["metadata"]
    assert vectors[0]["metadata"]["subject"] == "Physics"

def test_pinecone_service_sync_skips_already_indexed():
    mock_db = MagicMock()
    mock_vector_repo = MagicMock()
    mock_embedding_service = MagicMock()

    # Two questions in MongoDB
    q1 = QuestionResponse(
        question_id="Q1",
        paper_id="P1",
        question_number=1,
        content="Q1 content",
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
        content="Q2 content",
        subject="Chemistry",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = [q1.model_dump(by_alias=True), q2.model_dump(by_alias=True)]
    mock_db.questions.find.return_value = mock_cursor

    # Q1 is already indexed in Pinecone
    mock_vector_repo.get_existing_question_ids.return_value = {"Q1"}
    mock_vector_repo.upsert_records.return_value = 1

    mock_embedding_service.embed_questions.return_value = [
        {
            "question_id": "Q2",
            "embedding": [0.1] * 384,
            "payload": {"question_id": "Q2", "subject": "Chemistry"}
        }
    ]

    service = PineconeService(
        db=mock_db,
        vector_repo=mock_vector_repo,
        embedding_service=mock_embedding_service
    )

    result = service.sync_paper_vectors(paper_id="P1", batch_size=10, force_reindex=False)

    assert result["total_questions"] == 2
    assert result["already_indexed"] == 1
    assert result["newly_indexed"] == 1
    assert result["failed"] == 0

    mock_embedding_service.embed_questions.assert_called_once()
    mock_vector_repo.upsert_records.assert_called_once()
