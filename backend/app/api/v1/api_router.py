from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    ingestion,
    search,
    ai,
    questions,
    papers,
    practice,
    analytics,
    mistakes,
    recommendations,
    knowledge
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["Ingestion"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Tutoring"])
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
api_router.include_router(papers.router, prefix="/papers", tags=["Papers"])
api_router.include_router(practice.router, prefix="/practice", tags=["Practice Mode"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Performance Analytics"])
api_router.include_router(mistakes.router, prefix="/mistakes", tags=["Mistake Notebook"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Personalized Recommendations"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Graph Layer"])
