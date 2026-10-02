from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import logging
from app.schemas.analytics_schema import (
    AnalyticsSummaryResponse,
    SubjectAnalyticsItem,
    ChapterAnalyticsItem,
    ConceptAnalyticsItem,
    WeaknessResponse
)
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger("qnexus.api.analytics")

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummaryResponse, summary="Get Performance Summary")
def get_performance_summary():
    """
    Returns overall user performance metrics (accuracy, attempts, correct, incorrect,
    average time, sessions, and difficulty breakdown) via MongoDB aggregation.
    """
    try:
        service = AnalyticsService()
        return service.get_summary()
    except Exception as e:
        logger.error(f"Failed to calculate analytics summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analytics summary error: {str(e)}")

@router.get("/subjects", response_model=List[SubjectAnalyticsItem], summary="Get Subject-wise Performance")
def get_subject_performance():
    """
    Returns attempt counts and accuracy percentages grouped by Subject.
    """
    try:
        service = AnalyticsService()
        return service.get_subject_analytics()
    except Exception as e:
        logger.error(f"Failed to calculate subject analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Subject analytics error: {str(e)}")

@router.get("/chapters", response_model=List[ChapterAnalyticsItem], summary="Get Chapter-wise Performance")
def get_chapter_performance(
    subject: Optional[str] = Query(None, description="Optional subject filter e.g. Physics")
):
    """
    Returns attempt counts and accuracy percentages grouped by Chapter.
    """
    try:
        service = AnalyticsService()
        return service.get_chapter_analytics(subject=subject)
    except Exception as e:
        logger.error(f"Failed to calculate chapter analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chapter analytics error: {str(e)}")

@router.get("/concepts", response_model=List[ConceptAnalyticsItem], summary="Get Concept-wise Performance")
def get_concept_performance(
    subject: Optional[str] = Query(None, description="Optional subject filter"),
    chapter: Optional[str] = Query(None, description="Optional chapter filter")
):
    """
    Returns attempt counts and accuracy percentages grouped by Concept.
    """
    try:
        service = AnalyticsService()
        return service.get_concept_analytics(subject=subject, chapter=chapter)
    except Exception as e:
        logger.error(f"Failed to calculate concept analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Concept analytics error: {str(e)}")

@router.get("/weaknesses", response_model=WeaknessResponse, summary="Get Rule-Based Weakness Detection")
def get_weakness_detection(
    min_attempts: int = Query(3, ge=1, description="Minimum attempts required for evaluation"),
    weak_threshold: float = Query(60.0, ge=0.0, le=100.0, description="Accuracy % below which concept is considered weak"),
    subject: Optional[str] = Query(None, description="Optional subject filter")
):
    """
    Evaluates rule-based weakness detection on concepts:
    attempts >= min_attempts AND accuracy < weak_threshold.
    """
    try:
        service = AnalyticsService()
        return service.get_weaknesses(
            min_attempts=min_attempts,
            weak_threshold=weak_threshold,
            subject=subject
        )
    except Exception as e:
        logger.error(f"Failed to detect weaknesses: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Weakness detection error: {str(e)}")
