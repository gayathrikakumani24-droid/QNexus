from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from app.core.database import get_mongo_db
from app.repositories.paper_repository import PaperRepository
from app.schemas.paper_schema import PaperResponse
import logging

logger = logging.getLogger("qnexus.api.papers")

router = APIRouter()

@router.get("", response_model=List[PaperResponse], summary="List all ingested JEE Main papers")
def list_papers(
    year: Optional[int] = Query(None, description="Filter by exam year e.g. 2024, 2025, 2026"),
    session: Optional[str] = Query(None, description="Filter by session e.g. January, April"),
    shift: Optional[str] = Query(None, description="Filter by shift e.g. Shift 1, Shift 2"),
    limit: int = Query(100, ge=1, le=200, description="Max papers to return"),
    skip: int = Query(0, ge=0, description="Number of papers to skip")
):
    """
    Returns list of all shift-wise question papers stored in MongoDB across all years.
    """
    try:
        db = get_mongo_db()
        repo = PaperRepository(db)
        return repo.list_papers(year=year, session=session, shift=shift, limit=limit, skip=skip)
    except Exception as e:
        logger.error(f"Failed to list papers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{paper_id}", response_model=PaperResponse, summary="Get details for a single paper")
def get_paper(paper_id: str):
    """
    Returns metadata for a specific question paper.
    """
    try:
        db = get_mongo_db()
        repo = PaperRepository(db)
        paper = repo.get_paper(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found")
        return paper
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve paper {paper_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
