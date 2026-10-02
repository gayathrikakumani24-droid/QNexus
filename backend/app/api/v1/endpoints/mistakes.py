from fastapi import APIRouter, Query, HTTPException, Path
from typing import List, Optional
import logging
from app.schemas.mistake_schema import (
    MistakeCreateRequest,
    MistakeUpdateRequest,
    MistakeResponse,
    MistakeListResponse
)
from app.services.mistake_service import MistakeService

logger = logging.getLogger("qnexus.api.mistakes")

router = APIRouter()

@router.post("", response_model=MistakeResponse, summary="Save Question as Mistake")
def create_mistake(request: MistakeCreateRequest):
    """
    Saves or bookmarks a question as an error/mistake with tags and notes for spaced repetition.
    """
    try:
        service = MistakeService()
        return service.create_mistake(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create mistake: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Mistake creation error: {str(e)}")

@router.get("", response_model=MistakeListResponse, summary="List Mistake Notebook Records")
def list_mistakes(
    user_id: Optional[str] = Query("default_user", description="User ID"),
    subject: Optional[str] = Query(None, description="Subject filter e.g. Physics, Chemistry, Mathematics"),
    chapter: Optional[str] = Query(None, description="Chapter filter"),
    mistake_tag: Optional[str] = Query(None, description="Tag filter e.g. Calculation Error, Conceptual Gap"),
    review_status: Optional[str] = Query(None, description="Review status filter e.g. Needs Review, Reviewed, Mastered"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    Retrieves mistake records with filters and hydrated question statements.
    """
    try:
        service = MistakeService()
        return service.list_mistakes(
            user_id=user_id,
            subject=subject,
            chapter=chapter,
            mistake_tag=mistake_tag,
            review_status=review_status,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Failed to list mistakes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Mistake listing error: {str(e)}")

@router.patch("/{mistake_id}", response_model=MistakeResponse, summary="Update Mistake Notes, Tag or Status")
def update_mistake(
    mistake_id: str = Path(..., description="Mistake unique identifier"),
    request: MistakeUpdateRequest = ...
):
    """
    Updates mistake tag, candidate notes, or review status (Needs Review / Reviewed / Mastered).
    """
    try:
        service = MistakeService()
        return service.update_mistake(mistake_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update mistake {mistake_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Mistake update error: {str(e)}")

@router.delete("/{mistake_id}", summary="Delete Mistake Record")
def delete_mistake(mistake_id: str = Path(..., description="Mistake unique identifier")):
    """
    Removes a question from the candidate's mistake notebook.
    """
    try:
        service = MistakeService()
        service.delete_mistake(mistake_id)
        return {"status": "ok", "deleted": True, "mistake_id": mistake_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete mistake {mistake_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Mistake deletion error: {str(e)}")
