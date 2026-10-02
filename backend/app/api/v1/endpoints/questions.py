from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.question_schema import QuestionResponse
from app.schemas.search_schema import SearchResultItem
from app.core.database import get_mongo_db
from app.repositories.question_repository import QuestionRepository
from app.services.ai_service import AIService
import logging

logger = logging.getLogger("qnexus.api.questions")

router = APIRouter()

@router.get("/{question_id}", response_model=QuestionResponse, summary="Get Question by ID")
def get_question(question_id: str):
    """
    Fetches the authoritative question document from MongoDB by stable question_id.
    """
    db = get_mongo_db()
    repo = QuestionRepository(db)
    question = repo.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail=f"Question with ID '{question_id}' not found.")
    return question

@router.get("/{question_id}/similar", response_model=List[SearchResultItem], summary="Get Similar PYQs")
def get_similar_questions(
    question_id: str,
    top_k: int = Query(5, ge=1, le=20, description="Number of similar questions to retrieve")
):
    """
    Retrieves semantically similar previous year questions using Pinecone Cloud vector similarity.
    Excludes the query question itself and hydrates full documents from MongoDB.
    """
    try:
        service = AIService()
        similar_items = service.get_similar_questions(question_id=question_id, top_k=top_k)
        return similar_items
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to find similar questions for {question_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Similar questions service error: {str(e)}")

@router.get("", response_model=List[QuestionResponse], summary="List Questions with Metadata Filters")
def list_questions(
    subject: Optional[str] = Query(None),
    chapter: Optional[str] = Query(None),
    concept: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    shift: Optional[str] = Query(None),
    paper_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Lists questions with faceted metadata filters directly from MongoDB.
    """
    db = get_mongo_db()
    repo = QuestionRepository(db)
    return repo.list_questions(
        subject=subject,
        chapter=chapter,
        concept=concept,
        difficulty=difficulty,
        year=year,
        shift=shift,
        paper_id=paper_id,
        limit=limit,
        skip=skip
    )
