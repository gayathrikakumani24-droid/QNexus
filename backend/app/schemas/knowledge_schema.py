from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from app.schemas.question_schema import QuestionResponse

class ConceptKnowledgeResponse(BaseModel):
    concept: str = Field(..., description="Target concept name")
    chapter: str = Field(..., description="Parent chapter")
    subject: Optional[str] = Field(None, description="Parent subject e.g. Physics, Chemistry, Mathematics")
    related_questions: List[QuestionResponse] = Field(default_factory=list, description="Questions directly testing this concept")
    similar_concepts: List[str] = Field(default_factory=list, description="Related or co-occurring concepts in the syllabus")
    prerequisites: List[str] = Field(default_factory=list, description="Foundational prerequisite concepts required for mastery")

class ChapterHierarchyNode(BaseModel):
    chapter: str
    concepts: List[str] = Field(default_factory=list)

class SubjectHierarchyNode(BaseModel):
    subject: str
    chapters: List[ChapterHierarchyNode] = Field(default_factory=list)

class KnowledgeHierarchyResponse(BaseModel):
    hierarchy: List[SubjectHierarchyNode] = Field(default_factory=list)
