from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class PaperBase(BaseModel):
    paper_id: str = Field(..., description="Stable string ID e.g. JEE_MAIN_2026_APRIL_SHIFT_2")
    exam: str = Field("JEE Main", description="Exam name")
    year: int = Field(..., description="Exam year")
    session: str = Field(..., description="Exam session e.g. January or April")
    date: str = Field(..., description="Exam date YYYY-MM-DD")
    shift: str = Field(..., description="Shift name e.g. Shift 1 or Shift 2")
    filename: str = Field(..., description="Original PDF file name")
    total_questions: Optional[int] = Field(None, description="Total extracted questions count")
    status: str = Field("UPLOADED", description="UPLOADED, PROCESSING, PROCESSED, FAILED")

class PaperCreate(PaperBase):
    pass

class PaperUpdateStatus(BaseModel):
    status: str
    total_questions: Optional[int] = None

class PaperInDB(PaperBase):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(..., alias="_id", description="MongoDB _id set to paper_id")
    created_at: datetime = Field(default_factory=utc_now)

class PaperResponse(PaperBase):
    created_at: datetime = Field(default_factory=utc_now)
