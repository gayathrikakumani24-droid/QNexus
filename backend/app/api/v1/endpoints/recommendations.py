from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import logging
from app.schemas.recommendation_schema import RecommendationResponse
from app.services.recommendation_service import RecommendationService

logger = logging.getLogger("qnexus.api.recommendations")

router = APIRouter()

@router.get("", response_model=RecommendationResponse, summary="Get Personalized Practice Recommendations")
def get_personalized_recommendations(
    user_id: Optional[str] = Query("default_user", description="Student user identifier"),
    subject: Optional[str] = Query(None, description="Optional subject filter e.g. Physics, Chemistry, Mathematics"),
    limit: int = Query(10, ge=1, le=30, description="Number of recommendations to return")
):
    """
    Retrieves personalized, explainable question recommendations based strictly on actual student performance,
    conceptual accuracy diagnostics, and Pinecone Cloud vector retrieval.
    Excludes previously solved questions and automatically selects appropriate difficulty levels.
    """
    try:
        service = RecommendationService()
        return service.get_recommendations(
            user_id=user_id,
            subject=subject,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Recommendation generation error: {str(e)}")
