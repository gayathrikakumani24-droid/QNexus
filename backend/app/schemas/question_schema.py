from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class QuestionOption(BaseModel):
    id: str = Field(..., description="Option label, e.g. A, B, C, D")
    content: str = Field(..., description="Option text or LaTeX expression")

class QuestionBase(BaseModel):
    question_id: str = Field(..., description="Deterministic, unique string ID e.g. JEE_MAIN_2026_APRIL_SHIFT_2_Q01")
    paper_id: str = Field(..., description="Parent paper ID reference")
    question_number: int = Field(..., description="1-indexed question number")
    content: str = Field(..., description="Question statement text with LaTeX formatting")
    options: List[QuestionOption] = Field(default_factory=list)
    correct_option: Optional[str] = Field(None, description="Correct option label e.g. A, B, C, D")
    numerical_answer: Optional[float] = Field(None, description="Numerical answer value if applicable")
    official_solution: Optional[str] = Field(None, description="Step-by-step solution text")

    subject: Optional[str] = Field(None, description="Physics, Chemistry, or Mathematics")
    chapter: Optional[str] = Field(None, description="Topic/Chapter name")
    concept: Optional[str] = Field(None, description="Specific concept name")
    difficulty: Optional[str] = Field(None, description="Easy, Medium, or Hard")
    question_type: Optional[str] = Field(None, description="MCQ or Numerical")

    has_images: bool = Field(False, description="Whether question contains embedded diagram images")
    image_urls: List[str] = Field(default_factory=list)

    page_number: Optional[int] = Field(None, description="Page number in original PDF paper")

    year: int = Field(..., description="Exam year")
    session: str = Field(..., description="Exam session")
    date: str = Field(..., description="Exam date YYYY-MM-DD")
    shift: str = Field(..., description="Shift name")
    exam: Optional[str] = Field("JEE Main", description="Exam name e.g. JEE Main")

    answer: Optional[dict] = Field(None, description="Structured answer representation with raw value and typed metadata")
    metadata: Optional[dict] = Field(None, description="Source and audit metadata for the question and answer key")

    @property
    def question_text(self) -> str:
        return self.content

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdateMetadata(BaseModel):
    subject: Optional[str] = None
    chapter: Optional[str] = None
    concept: Optional[str] = None
    difficulty: Optional[str] = None
    question_type: Optional[str] = None
    correct_option: Optional[str] = None
    numerical_answer: Optional[float] = None
    official_solution: Optional[str] = None

class QuestionInDB(QuestionBase):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., alias="_id", description="MongoDB _id set to question_id")
    created_at: datetime = Field(default_factory=utc_now)

class QuestionResponse(QuestionBase):
    created_at: datetime = Field(default_factory=utc_now)
