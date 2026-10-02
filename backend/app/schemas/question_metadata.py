from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional

AllowedSubject = Literal["Physics", "Chemistry", "Mathematics", "Unknown"]
AllowedDifficulty = Literal["Easy", "Medium", "Hard", "Unknown"]
AllowedQuestionType = Literal["MCQ", "Numerical", "Assertion Reason", "Multiple Correct", "Unknown"]

class QuestionMetadata(BaseModel):
    subject: AllowedSubject = Field("Unknown", description="Subject: Physics, Chemistry, Mathematics, or Unknown")
    chapter: str = Field("Unknown", description="Chapter / Topic name")
    concept: str = Field("Unknown", description="Specific concept name")
    difficulty: AllowedDifficulty = Field("Unknown", description="Easy, Medium, Hard, or Unknown")
    question_type: AllowedQuestionType = Field("Unknown", description="MCQ, Numerical, Assertion Reason, Multiple Correct, or Unknown")

    @field_validator("subject", mode="before")
    def validate_subject(cls, v):
        if not v or not isinstance(v, str):
            return "Unknown"
        v_clean = v.strip().title()
        if v_clean in ["Physics", "Chemistry", "Mathematics"]:
            return v_clean
        if "phys" in v_clean.lower():
            return "Physics"
        if "chem" in v_clean.lower():
            return "Chemistry"
        if "math" in v_clean.lower():
            return "Mathematics"
        return "Unknown"

    @field_validator("difficulty", mode="before")
    def validate_difficulty(cls, v):
        if not v or not isinstance(v, str):
            return "Unknown"
        v_clean = v.strip().title()
        if v_clean in ["Easy", "Medium", "Hard"]:
            return v_clean
        return "Unknown"

    @field_validator("question_type", mode="before")
    def validate_question_type(cls, v):
        if not v or not isinstance(v, str):
            return "Unknown"
        v_clean = v.strip()
        v_upper = v_clean.upper()
        if v_upper == "MCQ":
            return "MCQ"
        if "NUMERICAL" in v_upper:
            return "Numerical"
        if "ASSERTION" in v_upper:
            return "Assertion Reason"
        if "MULTIPLE" in v_upper:
            return "Multiple Correct"
        return "Unknown"

class ClassificationSummaryResponse(BaseModel):
    paper_id: str = Field(..., description="Paper ID classified")
    processed: int = Field(..., description="Total questions examined in paper")
    successful: int = Field(..., description="Successfully classified questions count")
    failed: int = Field(0, description="Failed classification count")
