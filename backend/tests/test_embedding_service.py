import pytest
import math
from app.services.embedding_service import EmbeddingService
from app.schemas.question_schema import QuestionResponse

def test_format_question_for_embedding():
    formatted = EmbeddingService.format_question_for_embedding(
        content="Find moment of inertia about axis L.",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Parallel Axis Theorem"
    )
    assert "Subject: Physics" in formatted
    assert "Chapter: Rotational Motion" in formatted
    assert "Concept: Parallel Axis Theorem" in formatted
    assert "Question: Find moment of inertia about axis L." in formatted

def test_embedding_dimensions_and_normalization():
    service = EmbeddingService()
    text = "Find angular momentum of uniform cylinder rotating about its axis."
    
    embedding = service.embed_text(text)
    
    # 384 dimensions for all-MiniLM-L6-v2
    assert len(embedding) == 384
    
    # L2 norm should be approximately 1.0 (normalized for cosine similarity)
    norm = math.sqrt(sum(x * x for x in embedding))
    assert pytest.approx(norm, 0.01) == 1.0

def test_embed_texts_batch():
    service = EmbeddingService()
    texts = [
        "Calculate work done in isothermal expansion of ideal gas.",
        "Identify hybridisation of central atom in SF6.",
        "Find the value of definite integral from 0 to pi/2 of sin(x) dx."
    ]
    
    embeddings = service.embed_texts(texts, batch_size=2)
    assert len(embeddings) == 3
    for emb in embeddings:
        assert len(emb) == 384

def test_embed_questions_skip_existing():
    service = EmbeddingService()
    
    q1 = QuestionResponse(
        question_id="JEE_MAIN_2026_04_04_S1_Q_1",
        paper_id="JEE_MAIN_2026_04_04_S1",
        question_number=1,
        content="Find kinetic energy of rotating disc.",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Kinetic Energy",
        difficulty="Easy",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    q2 = QuestionResponse(
        question_id="JEE_MAIN_2026_04_04_S1_Q_2",
        paper_id="JEE_MAIN_2026_04_04_S1",
        question_number=2,
        content="Solve quadratic equation with real roots.",
        subject="Mathematics",
        chapter="Quadratic Equations",
        concept="Roots of Quadratic",
        difficulty="Medium",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    # If Q1 is already in existing_vector_ids, only Q2 should be embedded
    existing_ids = {"JEE_MAIN_2026_04_04_S1_Q_1"}
    records = service.embed_questions([q1, q2], existing_vector_ids=existing_ids)
    
    assert len(records) == 1
    assert records[0]["question_id"] == "JEE_MAIN_2026_04_04_S1_Q_2"
    assert len(records[0]["embedding"]) == 384
    assert records[0]["payload"]["subject"] == "Mathematics"
