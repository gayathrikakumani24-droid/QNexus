from fastapi import APIRouter, Path, HTTPException
import logging
from app.schemas.knowledge_schema import ConceptKnowledgeResponse, KnowledgeHierarchyResponse
from app.services.knowledge_service import KnowledgeService

logger = logging.getLogger("qnexus.api.knowledge")

router = APIRouter()

@router.get("/concept/{concept}", response_model=ConceptKnowledgeResponse, summary="Get Concept Knowledge Graph & Prerequisites")
def get_concept_knowledge(
    concept: str = Path(..., description="Name of the concept e.g. Torque, Moment of Inertia, Definite Integrals")
):
    """
    Retrieves the concept relationship layer:
    - Subject and Chapter associations
    - Related real questions testing this concept
    - Similar and co-occurring concepts in the syllabus
    - Foundational prerequisite concepts required for mastery
    """
    try:
        service = KnowledgeService()
        return service.get_concept_knowledge(concept)
    except Exception as e:
        logger.error(f"Failed to retrieve concept knowledge for '{concept}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Knowledge retrieval error: {str(e)}")

@router.get("/hierarchy", response_model=KnowledgeHierarchyResponse, summary="Get Subject -> Chapter -> Concept Hierarchy Tree")
def get_syllabus_hierarchy():
    """
    Retrieves the complete Subject -> Chapter -> Concept hierarchy derived from ingested JEE Main PYQs.
    """
    try:
        service = KnowledgeService()
        return service.get_syllabus_hierarchy()
    except Exception as e:
        logger.error(f"Failed to retrieve hierarchy tree: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Hierarchy retrieval error: {str(e)}")
