from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.question_schema import QuestionResponse

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    subject: Optional[str] = Field(None, description="Subject filter e.g. Physics, Chemistry, Mathematics")
    chapter: Optional[str] = Field(None, description="Chapter filter")
    concept: Optional[str] = Field(None, description="Concept filter")
    difficulty: Optional[str] = Field(None, description="Difficulty filter e.g. Easy, Medium, Hard")
    year: Optional[int] = Field(None, description="Year filter e.g. 2026")
    session: Optional[str] = Field(None, description="Session filter e.g. April or January")
    shift: Optional[str] = Field(None, description="Shift filter e.g. Shift 1 or Shift 2")
    top_k: int = Field(100, ge=1, le=200, description="Maximum number of results to return")
    min_score: Optional[float] = Field(0.30, ge=0.0, le=1.0, description="Minimum cosine similarity score threshold to filter relevant questions")

class SearchResultItem(BaseModel):
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    question: QuestionResponse = Field(..., description="Complete question document hydrated from MongoDB")

class SearchResponse(BaseModel):
    query: str
    total_found: int
    results: List[SearchResultItem] = Field(default_factory=list)
