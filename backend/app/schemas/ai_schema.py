from pydantic import BaseModel, Field
from typing import List, Optional

class ExplainRequest(BaseModel):
    question_id: str = Field(..., description="Target question ID to explain")
    user_attempt: Optional[str] = Field(None, description="Optional student selected option or numerical answer")

class ExplainResponse(BaseModel):
    question_id: str
    concept_summary: str = Field(..., description="Core concept and fundamental laws applied")
    step_by_step_solution: str = Field(..., description="Comprehensive step-by-step derivation with LaTeX")
    key_formulae: List[str] = Field(default_factory=list, description="Key equations used in the problem")
    common_pitfalls: Optional[str] = Field(None, description="Common traps and calculation mistakes to avoid")

class HintRequest(BaseModel):
    question_id: str = Field(..., description="Target question ID")
    hint_level: int = Field(1, ge=1, le=3, description="1: Conceptual direction, 2: Formula setup, 3: Next mathematical step")

class HintResponse(BaseModel):
    question_id: str
    hint_level: int
    hint_text: str = Field(..., description="Progressive hint without revealing the final option/answer")
    next_hint_available: bool
