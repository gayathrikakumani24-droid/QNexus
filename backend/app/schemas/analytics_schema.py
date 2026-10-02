from pydantic import BaseModel, Field
from typing import List, Optional

class DifficultyBreakdown(BaseModel):
    difficulty: str
    total_attempts: int = 0
    attempted: int = 0
    correct: int = 0
    incorrect: int = 0
    accuracy_percentage: float = 0.0

class AnalyticsSummaryResponse(BaseModel):
    overall_accuracy: float = 0.0
    total_questions_practiced: int = 0
    attempted: int = 0
    correct: int = 0
    incorrect: int = 0
    unanswered: int = 0
    average_time_seconds: float = 0.0
    total_sessions: int = 0
    difficulty_breakdown: List[DifficultyBreakdown] = Field(default_factory=list)

class SubjectAnalyticsItem(BaseModel):
    subject: str
    total_attempts: int = 0
    attempted: int = 0
    correct: int = 0
    incorrect: int = 0
    unanswered: int = 0
    accuracy_percentage: float = 0.0
    average_time_seconds: float = 0.0

class ChapterAnalyticsItem(BaseModel):
    subject: Optional[str] = None
    chapter: str
    total_attempts: int = 0
    attempted: int = 0
    correct: int = 0
    incorrect: int = 0
    unanswered: int = 0
    accuracy_percentage: float = 0.0
    average_time_seconds: float = 0.0

class ConceptAnalyticsItem(BaseModel):
    subject: Optional[str] = None
    chapter: Optional[str] = None
    concept: str
    total_attempts: int = 0
    attempted: int = 0
    correct: int = 0
    incorrect: int = 0
    unanswered: int = 0
    accuracy_percentage: float = 0.0
    average_time_seconds: float = 0.0

class WeaknessItem(BaseModel):
    subject: Optional[str] = None
    chapter: Optional[str] = None
    concept: str
    attempts: int = 0
    correct: int = 0
    incorrect: int = 0
    accuracy_percentage: float = 0.0
    severity: str = "Needs Practice"
    recommendation: str = ""

class WeaknessResponse(BaseModel):
    total_weaknesses_found: int = 0
    minimum_attempts_rule: int = 3
    weak_accuracy_threshold: float = 60.0
    weaknesses: List[WeaknessItem] = Field(default_factory=list)
