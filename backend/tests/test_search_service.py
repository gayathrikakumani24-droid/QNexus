import pytest
from unittest.mock import MagicMock
from app.services.search_service import SearchService
from app.schemas.search_schema import SearchRequest
from app.schemas.question_schema import QuestionResponse

def test_search_service_pipeline_success():
    mock_db = MagicMock()
    mock_embedding_service = MagicMock()
    mock_pinecone = MagicMock()

    # 1. Query vector returned by embedding service
    mock_embedding_service.embed_text.return_value = [0.05] * 384

    # 2. Pinecone returns two nearest matches
    hit1 = MagicMock()
    hit1.score = 0.8923
    hit1.metadata = {"question_id": "Q_ROT_1"}

    hit2 = MagicMock()
    hit2.score = 0.7412
    hit2.metadata = {"question_id": "Q_ROT_2"}

    mock_pinecone.query.return_value.matches = [hit1, hit2]

    # 3. MongoDB returns hydrated question documents
    q1 = QuestionResponse(
        question_id="Q_ROT_1",
        paper_id="P1",
        question_number=1,
        content="Calculate torque about origin.",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Torque",
        difficulty="Medium",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    q2 = QuestionResponse(
        question_id="Q_ROT_2",
        paper_id="P1",
        question_number=2,
        content="Find angular momentum of revolving particle.",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Angular Momentum",
        difficulty="Hard",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    # Return questions from MongoDB
    mock_db.questions.find.return_value = [q2.model_dump(by_alias=True), q1.model_dump(by_alias=True)]

    service = SearchService(
        db=mock_db,
        embedding_service=mock_embedding_service,
        pinecone_index=mock_pinecone
    )

    request = SearchRequest(
        query="medium questions involving torque and angular momentum",
        subject="Physics",
        difficulty="Medium",
        top_k=5
    )

    response = service.search_questions(request)

    assert response.total_found == 2
    assert len(response.results) == 2
    
    # Verify rank order preserved (Q_ROT_1 first, then Q_ROT_2)
    assert response.results[0].question.question_id == "Q_ROT_1"
    assert response.results[0].similarity_score == 0.8923
    assert response.results[0].question.subject == "Physics"

    assert response.results[1].question.question_id == "Q_ROT_2"
    assert response.results[1].similarity_score == 0.7412

    # Verify query was embedded but never sent to Groq
    mock_embedding_service.embed_text.assert_called_once_with("medium questions involving torque and angular momentum")
    mock_pinecone.query.assert_called_once()

def test_search_service_empty_results():
    mock_db = MagicMock()
    mock_embedding_service = MagicMock()
    mock_pinecone = MagicMock()

    mock_embedding_service.embed_text.return_value = [0.01] * 384
    mock_pinecone.query.return_value.matches = []

    service = SearchService(
        db=mock_db,
        embedding_service=mock_embedding_service,
        pinecone_index=mock_pinecone
    )

    request = SearchRequest(
        query="quantum entanglement in superconductors",
        subject="Chemistry",
        top_k=10
    )

    response = service.search_questions(request)

    assert response.total_found == 0
    assert len(response.results) == 0
    assert response.query == "quantum entanglement in superconductors"

def test_search_service_build_filter_conditions():
    service = SearchService(db=MagicMock(), embedding_service=MagicMock(), pinecone_index=MagicMock())
    
    request = SearchRequest(
        query="wave optics fringe width",
        subject="Physics",
        chapter="Wave Optics",
        concept="Young Double Slit",
        difficulty="Easy",
        year=2026,
        session="April",
        shift="Shift 2"
    )

    pinecone_filter = service._build_pinecone_filter(request)
    assert pinecone_filter is not None
    assert len(pinecone_filter) == 7
    assert pinecone_filter["subject"] == {"$eq": "Physics"}
    assert pinecone_filter["chapter"] == {"$eq": "Wave Optics"}
    assert pinecone_filter["concept"] == {"$eq": "Young Double Slit"}
    assert pinecone_filter["difficulty"] == {"$eq": "Easy"}
    assert pinecone_filter["year"] == {"$eq": 2026}
    assert pinecone_filter["session"] == {"$eq": "April"}
    assert pinecone_filter["shift"] == {"$eq": "Shift 2"}
