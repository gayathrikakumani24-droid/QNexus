from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from app.schemas.question_schema import QuestionResponse

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class MistakeCreateRequest(BaseModel):
    question_id: str
    user_id: str = Field("default_user", description="User identifier")
    subject: Optional[str] = None
    chapter: Optional[str] = None
    concept: Optional[str] = None
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    mistake_tag: str = Field("Conceptual Gap", description="Tag e.g. Calculation Error, Conceptual Gap, Formula Forgotten, Misread Question, Time Pressure, Silly Mistake")
    user_notes: Optional[str] = None
    review_status: str = Field("Needs Review", description="Review status: Needs Review, Reviewed, Mastered")

class MistakeUpdateRequest(BaseModel):
    mistake_tag: Optional[str] = None
    user_notes: Optional[str] = None
    review_status: Optional[str] = None

class MistakeResponse(BaseModel):
    mistake_id: str
    user_id: str
    question_id: str
    subject: Optional[str] = None
    chapter: Optional[str] = None
    concept: Optional[str] = None
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    mistake_tag: str = "Conceptual Gap"
    user_notes: Optional[str] = None
    review_status: str = "Needs Review"
    question: Optional[QuestionResponse] = None
    created_at: Optional[datetime] = Field(default_factory=utc_now)
    updated_at: Optional[datetime] = Field(default_factory=utc_now)

class MistakeListResponse(BaseModel):
    total: int
    mistakes: List[MistakeResponse] = Field(default_factory=list)
