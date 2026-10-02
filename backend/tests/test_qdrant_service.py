import pytest
from unittest.mock import MagicMock
from app.repositories.vector_repository import VectorRepository
from app.services.qdrant_service import QdrantService
from app.schemas.question_schema import QuestionResponse

def test_qdrant_service_sync_skips_already_indexed():
    mock_db = MagicMock()
    mock_vector_repo = MagicMock()
    mock_embedding_service = MagicMock()

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

    # Q1 is already indexed
    mock_vector_repo.get_existing_question_ids.return_value = {"Q1"}
    mock_vector_repo.upsert_records.return_value = 1

    mock_embedding_service.embed_questions.return_value = [
        {
            "question_id": "Q2",
            "embedding": [0.1] * 384,
            "payload": {"question_id": "Q2", "subject": "Chemistry"}
        }
    ]

    service = QdrantService(
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
