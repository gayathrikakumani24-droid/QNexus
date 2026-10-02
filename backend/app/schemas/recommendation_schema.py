from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.question_schema import QuestionResponse

class RecommendationItem(BaseModel):
    question_id: str
    subject: str
    chapter: str
    concept: str
    difficulty: str
    reason: str
    similarity_score: Optional[float] = None
    question: QuestionResponse

class RecommendationResponse(BaseModel):
    total: int
    user_id: str
    disclaimer: str = "Recommendations are generated deterministically based on your actual practice accuracy and conceptual weakness patterns. They do not predict future JEE Main exam questions."
    recommendations: List[RecommendationItem] = Field(default_factory=list)
