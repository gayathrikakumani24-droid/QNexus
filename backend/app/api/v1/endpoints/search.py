from fastapi import APIRouter, HTTPException
from app.schemas.search_schema import SearchRequest, SearchResponse
from app.services.search_service import SearchService
import logging

logger = logging.getLogger("qnexus.api.search")

router = APIRouter()

@router.post("", response_model=SearchResponse, summary="Semantic & Filtered PYQ Search")
def search_pyqs(request: SearchRequest):
    """
    Executes semantic vector search over previous year questions.
    Uses Sentence Transformers to encode query, Pinecone Cloud for semantic filtering,
    and hydrates complete question documents from MongoDB.
    """
    try:
        service = SearchService()
        response = service.search_questions(request)
        return response
    except Exception as e:
        logger.error(f"Semantic search endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
