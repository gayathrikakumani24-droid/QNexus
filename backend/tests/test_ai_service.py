import pytest
from unittest.mock import MagicMock
from app.services.ai_service import AIService
from app.schemas.question_schema import QuestionResponse

def test_explain_question_success():
    mock_db = MagicMock()
    mock_llm = MagicMock()

    q = QuestionResponse(
        question_id="Q_ROT_1",
        paper_id="P1",
        question_number=1,
        content="Find moment of inertia of solid sphere about tangent.",
        options=[{"id": "A", "content": "7/5 MR^2"}],
        correct_option="A",
        official_solution="Using parallel axis theorem: I = 2/5 MR^2 + MR^2 = 7/5 MR^2",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Parallel Axis Theorem",
        difficulty="Medium",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    mock_db.questions.find_one.return_value = q.model_dump(by_alias=True)

    mock_llm.generate_json_completion.return_value = {
        "concept_summary": "Parallel Axis Theorem applies to rigid bodies.",
        "step_by_step_solution": "Step 1: Calculate $I_{cm} = \\frac{2}{5}MR^2$.\nStep 2: Add $Md^2 = MR^2$.\nResult: $\\frac{7}{5}MR^2$.",
        "key_formulae": ["$I = I_{cm} + Md^2$"],
        "common_pitfalls": "Forgetting to square the distance parameter."
    }

    service = AIService(db=mock_db, llm_client=mock_llm)
    res = service.explain_question("Q_ROT_1", user_attempt="B")

    assert res.question_id == "Q_ROT_1"
    assert "Parallel Axis Theorem" in res.concept_summary
    assert len(res.key_formulae) == 1
    assert "Step 1" in res.step_by_step_solution

    # Verify MongoDB was NEVER modified/updated during explanation
    mock_db.questions.update_one.assert_not_called()
    mock_db.questions.find_one_and_update.assert_not_called()

def test_get_hint_progressive_levels():
    mock_db = MagicMock()
    mock_llm = MagicMock()

    q = QuestionResponse(
        question_id="Q_ROT_1",
        paper_id="P1",
        question_number=1,
        content="Find moment of inertia of solid sphere.",
        subject="Physics",
        chapter="Rotational Motion",
        concept="Parallel Axis Theorem",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    mock_db.questions.find_one.return_value = q.model_dump(by_alias=True)
    mock_llm.generate_json_completion.return_value = {
        "hint_text": "Recall the relation between moment of inertia about the center of mass and a parallel axis."
    }

    service = AIService(db=mock_db, llm_client=mock_llm)
    
    # Level 1 hint
    hint1 = service.get_hint("Q_ROT_1", hint_level=1)
    assert hint1.hint_level == 1
    assert hint1.next_hint_available is True
    assert "center of mass" in hint1.hint_text

    # Level 3 hint
    hint3 = service.get_hint("Q_ROT_1", hint_level=3)
    assert hint3.hint_level == 3
    assert hint3.next_hint_available is False

def test_get_similar_questions_excludes_target():
    mock_db = MagicMock()
    mock_llm = MagicMock()
    mock_embedding = MagicMock()
    mock_pinecone = MagicMock()

    target_q = QuestionResponse(
        question_id="Q_TARGET",
        paper_id="P1",
        question_number=1,
        content="Target question about torque.",
        subject="Physics",
        chapter="Rotational Motion",
        year=2026,
        session="April",
        date="2026-04-04",
        shift="Shift 1"
    )

    similar_q1 = QuestionResponse(
        question_id="Q_SIMILAR_1",
        paper_id="P2",
        question_number=14,
        content="Similar question on angular impulse.",
        subject="Physics",
        chapter="Rotational Motion",
        year=2025,
        session="January",
        date="2025-01-28",
        shift="Shift 2"
    )

    mock_db.questions.find_one.return_value = target_q.model_dump(by_alias=True)
    mock_embedding.embed_text.return_value = [0.1] * 384

    # Pinecone returns target question + similar question
    hit_target = MagicMock()
    hit_target.score = 1.0
    hit_target.metadata = {"question_id": "Q_TARGET"}

    hit_sim = MagicMock()
    hit_sim.score = 0.85
    hit_sim.metadata = {"question_id": "Q_SIMILAR_1"}

    mock_pinecone.query.return_value.matches = [hit_target, hit_sim]

    # Mock MongoDB batch find
    mock_db.questions.find.return_value = [similar_q1.model_dump(by_alias=True)]

    service = AIService(
        db=mock_db,
        llm_client=mock_llm,
        embedding_service=mock_embedding,
        pinecone_index=mock_pinecone
    )

    results = service.get_similar_questions("Q_TARGET", top_k=2)

    assert len(results) == 1
    assert results[0].question.question_id == "Q_SIMILAR_1"
    assert results[0].similarity_score == 0.85

    # Verify Groq was NOT called for similarity search
    mock_llm.generate_json_completion.assert_not_called()
