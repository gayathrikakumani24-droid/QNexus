from fastapi import APIRouter, HTTPException
from app.schemas.ai_schema import ExplainRequest, ExplainResponse, HintRequest, HintResponse
from app.services.ai_service import AIService
import logging

logger = logging.getLogger("qnexus.api.ai")

router = APIRouter()

@router.post("/explain", response_model=ExplainResponse, summary="Generate Step-by-Step AI Explanation")
def explain_question_endpoint(request: ExplainRequest):
    """
    Retrieves the question from MongoDB, builds controlled prompt context with verified solution data,
    and returns a structured pedagogical explanation via Groq LLM. Does NOT modify the stored question.
    """
    try:
        service = AIService()
        explanation = service.explain_question(
            question_id=request.question_id,
            user_attempt=request.user_attempt
        )
        return explanation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate explanation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Explanation service error: {str(e)}")

@router.post("/hint", response_model=HintResponse, summary="Generate Progressive AI Hint")
def hint_question_endpoint(request: HintRequest):
    """
    Generates non-spoiler, progressive hints (Level 1, 2, or 3) for the student without revealing the final answer.
    """
    try:
        service = AIService()
        hint = service.get_hint(
            question_id=request.question_id,
            hint_level=request.hint_level
        )
        return hint
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate hint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Hint service error: {str(e)}")
