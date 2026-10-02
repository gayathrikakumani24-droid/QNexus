import pytest
from unittest.mock import MagicMock
from app.services.analytics_service import AnalyticsService
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics_schema import AnalyticsSummaryResponse, WeaknessResponse

def test_summary_analytics_empty():
    mock_repo = MagicMock(spec=AnalyticsRepository)
    mock_repo.get_summary_aggregation.return_value = {
        "overall": [],
        "difficulty_breakdown": []
    }

    service = AnalyticsService(analytics_repo=mock_repo)
    summary = service.get_summary()

    assert isinstance(summary, AnalyticsSummaryResponse)
    assert summary.overall_accuracy == 0.0
    assert summary.attempted == 0
    assert summary.total_questions_practiced == 0
    assert len(summary.difficulty_breakdown) == 0

def test_summary_analytics_calculations():
    mock_repo = MagicMock(spec=AnalyticsRepository)
    mock_repo.get_summary_aggregation.return_value = {
        "overall": [{
            "total_questions_practiced": 10,
            "attempted": 8,
            "correct": 6,
            "incorrect": 2,
            "unanswered": 2,
            "total_time_seconds": 480,
            "unique_sessions": ["SESS_1", "SESS_2"]
        }],
        "difficulty_breakdown": [
            {
                "_id": "Easy",
                "total_attempts": 4,
                "attempted": 4,
                "correct": 4,
                "incorrect": 0
            },
            {
                "_id": "Hard",
                "total_attempts": 4,
                "attempted": 4,
                "correct": 2,
                "incorrect": 2
            }
        ]
    }

    service = AnalyticsService(analytics_repo=mock_repo)
    summary = service.get_summary()

    assert summary.total_questions_practiced == 10
    assert summary.attempted == 8
    assert summary.correct == 6
    assert summary.incorrect == 2
    assert summary.unanswered == 2
    assert summary.overall_accuracy == 75.0  # (6 / 8) * 100
    assert summary.average_time_seconds == 60.0  # 480 / 8
    assert summary.total_sessions == 2
    assert len(summary.difficulty_breakdown) == 2
    assert summary.difficulty_breakdown[0].difficulty == "Easy"
    assert summary.difficulty_breakdown[0].accuracy_percentage == 100.0
    assert summary.difficulty_breakdown[1].difficulty == "Hard"
    assert summary.difficulty_breakdown[1].accuracy_percentage == 50.0

def test_subject_analytics():
    mock_repo = MagicMock(spec=AnalyticsRepository)
    mock_repo.get_subject_aggregation.return_value = [
        {
            "_id": "Physics",
            "total_attempts": 10,
            "attempted": 10,
            "correct": 8,
            "incorrect": 2,
            "unanswered": 0,
            "total_time_seconds": 600
        },
        {
            "_id": "Mathematics",
            "total_attempts": 5,
            "attempted": 4,
            "correct": 1,
            "incorrect": 3,
            "unanswered": 1,
            "total_time_seconds": 360
        }
    ]

    service = AnalyticsService(analytics_repo=mock_repo)
    subjects = service.get_subject_analytics()

    assert len(subjects) == 2
    assert subjects[0].subject == "Physics"
    assert subjects[0].accuracy_percentage == 80.0
    assert subjects[0].average_time_seconds == 60.0

    assert subjects[1].subject == "Mathematics"
    assert subjects[1].accuracy_percentage == 25.0
    assert subjects[1].average_time_seconds == 90.0

def test_chapter_and_concept_analytics():
    mock_repo = MagicMock(spec=AnalyticsRepository)
    mock_repo.get_chapter_aggregation.return_value = [
        {
            "_id": {"subject": "Physics", "chapter": "Rotational Motion"},
            "total_attempts": 6,
            "attempted": 6,
            "correct": 3,
            "incorrect": 3,
            "unanswered": 0,
            "total_time_seconds": 300
        }
    ]
    mock_repo.get_concept_aggregation.return_value = [
        {
            "_id": {"subject": "Physics", "chapter": "Rotational Motion", "concept": "Moment of Inertia"},
            "total_attempts": 4,
            "attempted": 4,
            "correct": 1,
            "incorrect": 3,
            "unanswered": 0,
            "total_time_seconds": 240
        }
    ]

    service = AnalyticsService(analytics_repo=mock_repo)
    chapters = service.get_chapter_analytics(subject="Physics")
    concepts = service.get_concept_analytics(subject="Physics")

    assert len(chapters) == 1
    assert chapters[0].chapter == "Rotational Motion"
    assert chapters[0].accuracy_percentage == 50.0

    assert len(concepts) == 1
    assert concepts[0].concept == "Moment of Inertia"
    assert concepts[0].accuracy_percentage == 25.0

def test_rule_based_weakness_detection():
    mock_repo = MagicMock(spec=AnalyticsRepository)
    # Concept 1: 4 attempts, 25% accuracy -> Weak (< 60%) & Critical (< 40%)
    # Concept 2: 5 attempts, 80% accuracy -> Not weak (>= 60%)
    # Concept 3: 2 attempts, 0% accuracy -> Not weak because attempts < min_attempts (3)
    # Concept 4: 4 attempts, 50% accuracy -> Weak (< 60%) & Needs Practice (>= 40%)
    mock_repo.get_concept_aggregation.return_value = [
        {
            "_id": {"subject": "Physics", "chapter": "Rotational Motion", "concept": "Moment of Inertia"},
            "total_attempts": 4,
            "attempted": 4,
            "correct": 1,
            "incorrect": 3,
            "unanswered": 0,
            "total_time_seconds": 240
        },
        {
            "_id": {"subject": "Physics", "chapter": "Thermodynamics", "concept": "Carnot Engine"},
            "total_attempts": 5,
            "attempted": 5,
            "correct": 4,
            "incorrect": 1,
            "unanswered": 0,
            "total_time_seconds": 200
        },
        {
            "_id": {"subject": "Chemistry", "chapter": "Chemical Bonding", "concept": "Hybridization"},
            "total_attempts": 2,
            "attempted": 2,
            "correct": 0,
            "incorrect": 2,
            "unanswered": 0,
            "total_time_seconds": 90
        },
        {
            "_id": {"subject": "Mathematics", "chapter": "Calculus", "concept": "Definite Integrals"},
            "total_attempts": 4,
            "attempted": 4,
            "correct": 2,
            "incorrect": 2,
            "unanswered": 0,
            "total_time_seconds": 240
        }
    ]

    service = AnalyticsService(analytics_repo=mock_repo)
    weakness_res = service.get_weaknesses(min_attempts=3, weak_threshold=60.0)

    assert isinstance(weakness_res, WeaknessResponse)
    assert weakness_res.total_weaknesses_found == 2
    assert weakness_res.minimum_attempts_rule == 3
    assert weakness_res.weak_accuracy_threshold == 60.0

    w1 = weakness_res.weaknesses[0]
    assert w1.concept == "Moment of Inertia"
    assert w1.accuracy_percentage == 25.0
    assert w1.severity == "Critical"

    w2 = weakness_res.weaknesses[1]
    assert w2.concept == "Definite Integrals"
    assert w2.accuracy_percentage == 50.0
    assert w2.severity == "Needs Practice"
