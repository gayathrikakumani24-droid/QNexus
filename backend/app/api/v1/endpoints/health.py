from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthCheckResponse(BaseModel):
    status: str = "ok"
    service: str = "qnexus-backend"

@router.get("/health", response_model=HealthCheckResponse, summary="Health Check")
def get_health():
    """Returns application health status."""
    return HealthCheckResponse()
