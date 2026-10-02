from pydantic import BaseModel, Field
from typing import List, Optional

class IngestionResponse(BaseModel):
    paper_id: str = Field(..., description="Stable paper ID")
    status: str = Field(..., description="PROCESSED, FAILED, or UPLOADED")
    pages: int = Field(..., description="Total pages extracted from PDF")
    questions_extracted: int = Field(..., description="Total structured questions extracted")
    warnings: List[str] = Field(default_factory=list, description="Any warnings encountered during parsing")
