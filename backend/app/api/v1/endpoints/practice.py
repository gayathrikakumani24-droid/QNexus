from fastapi import APIRouter, HTTPException
from app.schemas.practice_schema import (
    PracticeStartRequest,
    PracticeStartResponse,
    PracticeAnswerRequest,
    PracticeSubmitResponse
)
from app.services.practice_service import PracticeService
import logging

logger = logging.getLogger("qnexus.api.practice")

router = APIRouter()

@router.post("/start", response_model=PracticeStartResponse, summary="Start Adaptive Practice Session")
def start_practice(request: PracticeStartRequest):
    """
    Initializes a new practice session using existing JEE Main questions from MongoDB.
    Does NOT generate synthetic questions.
    """
    try:
        service = PracticeService()
        return service.start_session(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start practice session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Practice session error: {str(e)}")

@router.post("/{session_id}/answer", summary="Record Question Answer")
def record_answer(session_id: str, request: PracticeAnswerRequest):
    """
    Records or updates a candidate's answer and review state for a question in an active session.
    """
    try:
        service = PracticeService()
        success = service.record_answer(session_id, request)
        return {"status": "ok", "saved": success}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to record answer for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Answer recording error: {str(e)}")

@router.post("/{session_id}/submit", response_model=PracticeSubmitResponse, summary="Submit & Evaluate Practice Session")
def submit_practice(session_id: str):
    """
    Evaluates all submitted answers against MongoDB keys, saves attempts to attempts collection,
    calculates JEE Main scores (+4/-1), and returns detailed result breakdown.
    """
    try:
        service = PracticeService()
        return service.submit_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to submit session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Submission evaluation error: {str(e)}")
