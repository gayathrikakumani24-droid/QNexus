import pytest
from unittest.mock import MagicMock
from app.services.knowledge_service import KnowledgeService
from app.repositories.knowledge_repository import BaseKnowledgeRepository
from app.schemas.knowledge_schema import ConceptKnowledgeResponse, KnowledgeHierarchyResponse

def test_get_concept_knowledge_returns_prerequisites_and_similar():
    mock_repo = MagicMock(spec=BaseKnowledgeRepository)

    mock_repo.get_concept_metadata.return_value = {
        "concept": "Torque",
        "chapter": "Rotational Motion",
        "subject": "Physics"
    }

    mock_repo.get_related_questions.return_value = [
        {
            "question_id": "JEE_MAIN_2026_01_24_S1_Q_01",
            "paper_id": "JEE_MAIN_2026_01_24_S1",
            "question_number": 1,
            "content": "A rod of length L has torque applied.",
            "subject": "Physics",
            "chapter": "Rotational Motion",
            "concept": "Torque",
            "year": 2026,
            "session": "January",
            "date": "2026-01-24",
            "shift": "Shift 1"
        }
    ]

    mock_repo.get_sibling_concepts_in_chapter.return_value = [
        "Moment of Inertia",
        "Angular Momentum",
        "Rolling Motion"
    ]

    service = KnowledgeService(knowledge_repo=mock_repo)
    res = service.get_concept_knowledge("Torque")

    assert isinstance(res, ConceptKnowledgeResponse)
    assert res.concept == "Torque"
    assert res.chapter == "Rotational Motion"
    assert res.subject == "Physics"
    assert len(res.related_questions) == 1
    assert res.related_questions[0].question_id == "JEE_MAIN_2026_01_24_S1_Q_01"
    assert "Moment of Inertia" in res.similar_concepts
    assert "Moment of Inertia" in res.prerequisites
    assert "Newton's Laws of Motion" in res.prerequisites

def test_get_concept_knowledge_fallback():
    mock_repo = MagicMock(spec=BaseKnowledgeRepository)

    mock_repo.get_concept_metadata.return_value = {
        "concept": "Custom Concept X",
        "chapter": "Custom Chapter",
        "subject": "Physics"
    }
    mock_repo.get_related_questions.return_value = []
    mock_repo.get_sibling_concepts_in_chapter.return_value = ["Sibling Concept A", "Sibling Concept B"]

    service = KnowledgeService(knowledge_repo=mock_repo)
    res = service.get_concept_knowledge("Custom Concept X")

    assert res.concept == "Custom Concept X"
    assert res.chapter == "Custom Chapter"
    assert len(res.prerequisites) > 0
    assert "Sibling Concept A" in res.prerequisites

def test_get_syllabus_hierarchy():
    mock_repo = MagicMock(spec=BaseKnowledgeRepository)

    mock_repo.get_hierarchy_tree.return_value = [
        {
            "_id": "Physics",
            "chapters": [
                {
                    "chapter": "Rotational Motion",
                    "concepts": ["Torque", "Moment of Inertia"]
                }
            ]
        }
    ]

    service = KnowledgeService(knowledge_repo=mock_repo)
    res = service.get_syllabus_hierarchy()

    assert isinstance(res, KnowledgeHierarchyResponse)
    assert len(res.hierarchy) == 1
    assert res.hierarchy[0].subject == "Physics"
    assert res.hierarchy[0].chapters[0].chapter == "Rotational Motion"
    assert "Torque" in res.hierarchy[0].chapters[0].concepts
