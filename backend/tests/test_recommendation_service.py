import pytest
from unittest.mock import MagicMock
from app.services.recommendation_service import RecommendationService
from app.repositories.question_repository import QuestionRepository
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.embedding_service import EmbeddingService
from app.schemas.question_schema import QuestionResponse
from app.schemas.recommendation_schema import RecommendationResponse

def test_recommendations_based_on_weak_concepts():
    mock_db = MagicMock()
    mock_question_repo = MagicMock(spec=QuestionRepository)
    mock_analytics_repo = MagicMock(spec=AnalyticsRepository)
    mock_embedding_service = MagicMock(spec=EmbeddingService)
    mock_pinecone_index = MagicMock()

    # User attempts: concept "Torque" has 52% accuracy (10 attempts, 5 correct, 5 incorrect)
    mock_analytics_repo.get_concept_aggregation.return_value = [
        {
            "_id": {"subject": "Physics", "chapter": "Rotational Motion", "concept": "Torque"},
            "total_attempts": 10,
            "attempted": 10,
            "correct": 5,
            "incorrect": 5,
            "unanswered": 0,
            "total_time_seconds": 600
        }
    ]

    # User already solved question Q_SOLVED
    mock_db.attempts.find.return_value = [{"question_id": "Q_SOLVED"}]
    mock_db.practice_sessions.find.return_value = []

    # Embedding service returns dummy vector
    mock_embedding_service.embed_text.return_value = [0.1] * 384

    # Pinecone returns 2 candidates: Q_SOLVED and Q_NEW
    hit_solved = MagicMock()
    hit_solved.metadata = {"question_id": "Q_SOLVED"}
    hit_solved.score = 0.95

    hit_new = MagicMock()
    hit_new.metadata = {"question_id": "Q_NEW"}
    hit_new.score = 0.88

    mock_pinecone_index.query.return_value.matches = [hit_solved, hit_new]

    # Question repo returns Q_NEW
    q_new_doc = QuestionResponse(
        question_id="Q_NEW",
        paper_id="PAPER_1",
        question_number=5,
        content="Calculate the torque about the origin.",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Torque",
        difficulty="Medium",
        correct_option="A",
        year=2026,
        session="January",
        date="2026-01-24",
        shift="Shift 1"
    )
    mock_question_repo.get_question.side_effect = lambda q_id: q_new_doc if q_id == "Q_NEW" else None
    mock_question_repo.list_questions.return_value = []

    service = RecommendationService(
        db=mock_db,
        question_repo=mock_question_repo,
        analytics_repo=mock_analytics_repo,
        embedding_service=mock_embedding_service,
        pinecone_index=mock_pinecone_index
    )

    res = service.get_recommendations(user_id="user_123", limit=5)

    assert isinstance(res, RecommendationResponse)
    assert res.total == 1
    assert res.recommendations[0].question_id == "Q_NEW"
    assert res.recommendations[0].concept == "Torque"
    assert "accuracy in Torque questions is 50.0%" in res.recommendations[0].reason
    assert "predict future JEE Main exam questions" in res.disclaimer

def test_recommendations_cold_start_fallback():
    mock_db = MagicMock()
    mock_question_repo = MagicMock(spec=QuestionRepository)
    mock_analytics_repo = MagicMock(spec=AnalyticsRepository)
    mock_embedding_service = MagicMock(spec=EmbeddingService)
    mock_pinecone_index = MagicMock()

    # 0 prior attempts
    mock_analytics_repo.get_concept_aggregation.return_value = []
    mock_db.attempts.find.return_value = []
    mock_db.practice_sessions.find.return_value = []

    fallback_q = QuestionResponse(
        question_id="Q_FALLBACK",
        paper_id="PAPER_1",
        question_number=1,
        content="State the first law of thermodynamics.",
        subject="Physics",
        chapter="Thermodynamics",
        concept="First Law",
        difficulty="Medium",
        year=2026,
        session="January",
        date="2026-01-24",
        shift="Shift 1"
    )
    mock_question_repo.list_questions.return_value = [fallback_q]

    service = RecommendationService(
        db=mock_db,
        question_repo=mock_question_repo,
        analytics_repo=mock_analytics_repo,
        embedding_service=mock_embedding_service,
        pinecone_index=mock_pinecone_index
    )

    res = service.get_recommendations(user_id="new_student", limit=1)

    assert res.total == 1
    assert res.recommendations[0].question_id == "Q_FALLBACK"
    assert "Recommended diagnostic question" in res.recommendations[0].reason
