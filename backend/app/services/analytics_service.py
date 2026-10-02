import logging
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from app.core.database import get_mongo_db
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics_schema import (
    AnalyticsSummaryResponse,
    DifficultyBreakdown,
    SubjectAnalyticsItem,
    ChapterAnalyticsItem,
    ConceptAnalyticsItem,
    WeaknessItem,
    WeaknessResponse
)

logger = logging.getLogger("qnexus.services.analytics")

class AnalyticsService:
    def __init__(
        self,
        db: Optional[Database] = None,
        analytics_repo: Optional[AnalyticsRepository] = None
    ):
        self.db = db if db is not None else get_mongo_db()
        self.repo = analytics_repo or AnalyticsRepository(self.db)

    def get_summary(self) -> AnalyticsSummaryResponse:
        """
        Calculates overall user performance metrics across all attempts in MongoDB.
        """
        agg = self.repo.get_summary_aggregation()
        overall_list = agg.get("overall", [])
        diff_list = agg.get("difficulty_breakdown", [])

        if not overall_list:
            return AnalyticsSummaryResponse()

        overall = overall_list[0]
        attempted = overall.get("attempted", 0)
        correct = overall.get("correct", 0)
        incorrect = overall.get("incorrect", 0)
        unanswered = overall.get("unanswered", 0)
        total_time = overall.get("total_time_seconds", 0)
        total_practiced = overall.get("total_questions_practiced", 0)
        unique_sessions = overall.get("unique_sessions", [])

        overall_accuracy = (
            round((correct / (correct + incorrect)) * 100, 1)
            if (correct + incorrect) > 0
            else 0.0
        )

        average_time = (
            round(total_time / attempted, 1)
            if attempted > 0
            else 0.0
        )

        # Build difficulty breakdown
        difficulty_breakdown: List[DifficultyBreakdown] = []
        for d in diff_list:
            d_name = d.get("_id") or "Unknown"
            d_total = d.get("total_attempts", 0)
            d_attempted = d.get("attempted", 0)
            d_correct = d.get("correct", 0)
            d_incorrect = d.get("incorrect", 0)
            d_acc = (
                round((d_correct / (d_correct + d_incorrect)) * 100, 1)
                if (d_correct + d_incorrect) > 0
                else 0.0
            )

            difficulty_breakdown.append(
                DifficultyBreakdown(
                    difficulty=d_name,
                    total_attempts=d_total,
                    attempted=d_attempted,
                    correct=d_correct,
                    incorrect=d_incorrect,
                    accuracy_percentage=d_acc
                )
            )

        return AnalyticsSummaryResponse(
            overall_accuracy=overall_accuracy,
            total_questions_practiced=total_practiced,
            attempted=attempted,
            correct=correct,
            incorrect=incorrect,
            unanswered=unanswered,
            average_time_seconds=average_time,
            total_sessions=len(unique_sessions),
            difficulty_breakdown=difficulty_breakdown
        )

    def get_subject_analytics(self) -> List[SubjectAnalyticsItem]:
        """
        Calculates accuracy and attempt counts for each Subject.
        """
        rows = self.repo.get_subject_aggregation()
        results: List[SubjectAnalyticsItem] = []

        for row in rows:
            subject = row.get("_id") or "Unknown"
            total = row.get("total_attempts", 0)
            attempted = row.get("attempted", 0)
            correct = row.get("correct", 0)
            incorrect = row.get("incorrect", 0)
            unanswered = row.get("unanswered", 0)
            total_time = row.get("total_time_seconds", 0)

            accuracy = (
                round((correct / (correct + incorrect)) * 100, 1)
                if (correct + incorrect) > 0
                else 0.0
            )

            avg_time = round(total_time / attempted, 1) if attempted > 0 else 0.0

            results.append(
                SubjectAnalyticsItem(
                    subject=subject,
                    total_attempts=total,
                    attempted=attempted,
                    correct=correct,
                    incorrect=incorrect,
                    unanswered=unanswered,
                    accuracy_percentage=accuracy,
                    average_time_seconds=avg_time
                )
            )

        return results

    def get_chapter_analytics(self, subject: Optional[str] = None) -> List[ChapterAnalyticsItem]:
        """
        Calculates accuracy and attempt counts for each Chapter.
        """
        rows = self.repo.get_chapter_aggregation(subject=subject)
        results: List[ChapterAnalyticsItem] = []

        for row in rows:
            group_id = row.get("_id", {})
            subj = group_id.get("subject", "Unknown")
            chapter = group_id.get("chapter", "General")
            total = row.get("total_attempts", 0)
            attempted = row.get("attempted", 0)
            correct = row.get("correct", 0)
            incorrect = row.get("incorrect", 0)
            unanswered = row.get("unanswered", 0)
            total_time = row.get("total_time_seconds", 0)

            accuracy = (
                round((correct / (correct + incorrect)) * 100, 1)
                if (correct + incorrect) > 0
                else 0.0
            )

            avg_time = round(total_time / attempted, 1) if attempted > 0 else 0.0

            results.append(
                ChapterAnalyticsItem(
                    subject=subj,
                    chapter=chapter,
                    total_attempts=total,
                    attempted=attempted,
                    correct=correct,
                    incorrect=incorrect,
                    unanswered=unanswered,
                    accuracy_percentage=accuracy,
                    average_time_seconds=avg_time
                )
            )

        return results

    def get_concept_analytics(
        self,
        subject: Optional[str] = None,
        chapter: Optional[str] = None
    ) -> List[ConceptAnalyticsItem]:
        """
        Calculates accuracy and attempt counts for each Concept.
        """
        rows = self.repo.get_concept_aggregation(subject=subject, chapter=chapter)
        results: List[ConceptAnalyticsItem] = []

        for row in rows:
            group_id = row.get("_id", {})
            subj = group_id.get("subject", "Unknown")
            chap = group_id.get("chapter", "General")
            concept = group_id.get("concept", "General Concepts")
            total = row.get("total_attempts", 0)
            attempted = row.get("attempted", 0)
            correct = row.get("correct", 0)
            incorrect = row.get("incorrect", 0)
            unanswered = row.get("unanswered", 0)
            total_time = row.get("total_time_seconds", 0)

            accuracy = (
                round((correct / (correct + incorrect)) * 100, 1)
                if (correct + incorrect) > 0
                else 0.0
            )

            avg_time = round(total_time / attempted, 1) if attempted > 0 else 0.0

            results.append(
                ConceptAnalyticsItem(
                    subject=subj,
                    chapter=chap,
                    concept=concept,
                    total_attempts=total,
                    attempted=attempted,
                    correct=correct,
                    incorrect=incorrect,
                    unanswered=unanswered,
                    accuracy_percentage=accuracy,
                    average_time_seconds=avg_time
                )
            )

        return results

    def get_weaknesses(
        self,
        min_attempts: int = 3,
        weak_threshold: float = 60.0,
        subject: Optional[str] = None
    ) -> WeaknessResponse:
        """
        Rule-based weakness detection engine.
        A concept is weak if:
            attempts >= minimum_attempts AND accuracy < weak_threshold

        Severity:
            Critical: accuracy < 40.0%
            Needs Practice: 40.0% <= accuracy < weak_threshold
        """
        concept_stats = self.get_concept_analytics(subject=subject)
        weaknesses: List[WeaknessItem] = []

        for c in concept_stats:
            # Rule Evaluation
            if c.attempted >= min_attempts and c.accuracy_percentage < weak_threshold:
                severity = "Critical" if c.accuracy_percentage < 40.0 else "Needs Practice"
                recommendation = (
                    f"Prioritize targeted PYQs in {c.chapter} focusing on {c.concept}. "
                    f"Current accuracy is {c.accuracy_percentage}% over {c.attempted} attempts."
                )

                weaknesses.append(
                    WeaknessItem(
                        subject=c.subject,
                        chapter=c.chapter,
                        concept=c.concept,
                        attempts=c.attempted,
                        correct=c.correct,
                        incorrect=c.incorrect,
                        accuracy_percentage=c.accuracy_percentage,
                        severity=severity,
                        recommendation=recommendation
                    )
                )

        # Sort by lowest accuracy first, then highest attempts
        weaknesses.sort(key=lambda w: (w.accuracy_percentage, -w.attempts))

        return WeaknessResponse(
            total_weaknesses_found=len(weaknesses),
            minimum_attempts_rule=min_attempts,
            weak_accuracy_threshold=weak_threshold,
            weaknesses=weaknesses
        )
