from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.schemas.question_schema import QuestionResponse, QuestionOption

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class PracticeStartRequest(BaseModel):
    subject: Optional[str] = Field(None, description="Subject filter e.g. Physics, Chemistry, Mathematics")
    chapter: Optional[str] = Field(None, description="Chapter filter")
    concept: Optional[str] = Field(None, description="Concept filter e.g. Moment of Inertia")
    difficulty: Optional[str] = Field(None, description="Difficulty filter e.g. Easy, Medium, Hard")
    year: Optional[int] = Field(None, description="Year filter e.g. 2026")
    session: Optional[str] = Field(None, description="Session filter e.g. April, January")
    shift: Optional[str] = Field(None, description="Shift filter e.g. Shift 1, Shift 2")
    paper_id: Optional[str] = Field(None, description="Paper ID filter")
    num_questions: int = Field(10, ge=1, le=50, description="Target number of questions for session")
    question_ids: Optional[List[str]] = Field(None, description="Explicit list of question IDs to practice (e.g. for mistake revision)")

class PracticeQuestionView(BaseModel):
    question_id: str
    paper_id: str
    question_number: int
    content: str
    options: List[QuestionOption] = Field(default_factory=list)
    subject: Optional[str] = None
    chapter: Optional[str] = None
    concept: Optional[str] = None
    difficulty: Optional[str] = None
    question_type: Optional[str] = None
    has_images: bool = False
    image_urls: List[str] = Field(default_factory=list)
    year: int
    session: str
    date: str
    shift: str

class PracticeStartResponse(BaseModel):
    session_id: str
    total_questions: int
    duration_minutes: int
    status: str = "IN_PROGRESS"
    questions: List[PracticeQuestionView]
    created_at: datetime = Field(default_factory=utc_now)

class PracticeAnswerRequest(BaseModel):
    question_id: str
    selected_answer: Optional[str] = Field(None, description="Selected option A, B, C, D or numerical value")
    time_spent_seconds: int = Field(0, ge=0)
    marked_for_review: bool = False

class AttemptRecord(BaseModel):
    question_id: str
    selected_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    time_spent_seconds: int = 0
    marked_for_review: bool = False
    attempted_at: datetime = Field(default_factory=utc_now)

class PracticeQuestionResult(BaseModel):
    question: QuestionResponse
    selected_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    is_correct: bool
    is_attempted: bool
    time_spent_seconds: int
    score_delta: int

class PracticeSubmitResponse(BaseModel):
    session_id: str
    total_questions: int
    attempted_count: int
    correct_count: int
    incorrect_count: int
    unattempted_count: int
    score: int
    max_score: int
    accuracy_percentage: float
    total_time_seconds: int
    status: str = "COMPLETED"
    results: List[PracticeQuestionResult]
    completed_at: datetime = Field(default_factory=utc_now)
